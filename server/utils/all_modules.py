import os
import fitz
import logging
from .pdf_url import *
from .translation import *
from fuzzywuzzy import fuzz
from .pdf_title_date import *
from pipeline import BASE_DIR
from server.utils import appLogger
from .pdftitle_algo import get_title_from_file

logger = logging.getLogger(__name__)

class Modules():

    def __init__(self, pdf, id):
        self.pdf = pdf
        self.id  = id
        self.doc = fitz.open(self.pdf)

    def fileStats_fun(self):
        
        logger = appLogger.get_logger(str(self.id))
        logger.info(f"DocumentsId:- {self.id} Started preocessing for fileStats module")
        try:

            doc = self.doc
            logger.info(f"DocumentsId:- {self.id} Successfully got reply from filestats module")
            return True, (doc.pageCount, metaDict[self.id])

        except Exception as e:

            logger.error(e)
            logger.error("Did not get reply from filestats module")
            return False, "problem to fetch filestats of document"


    # def docMeta_fun(self):

        from googletrans import Translator
        
        logger = appLogger.get_logger(str(self.id))
        logger.info(f"DocumentsId:- {self.id} Started preocessing for docMeta module")
        try:
            max_title = 10
            
            def CallPdftitle():
                c = get_title_from_file(self.pdf)
                words= c.split()
                listToStr = ' '.join([str(elem) for elem in words[0:max_title]])
                return listToStr

            def similarity(str_1,str_2):
                a = [0]
                for i in str_2: 
                    a.append(fuzz.ratio(str_1, i))
                if (max(a) >= 60):
                    return str_1
                else:
                    return "None"

            doc = self.doc
            
            try:
                # This function returns value of pdf Title(extract)
                if len(doc.metadata['title']) != 0:
                    text= doc[0].getText()
                    text_1 = text.split('\n')
                    title = similarity(doc.metadata['title'], text_1)
                    if title=='None':
                        title = CallPdftitle(self.pdf)
                else:
                    title = CallPdftitle(self.pdf)
            except:
                title = ""

            for page in doc.pages(0,1):
                pdf_text = page.getText("text")

            translator = Translator()
            lang = translator.translate(pdf_text)
            
            if (len(metaDict.get("modified_date")) == 0) | (len(str(title.replace(" ",""))) == 0) | (len(lang.src) == 0):
                return False, "docMeta failed"
            else:
                logger.info(f"DocumentsId:- {self.id} Successfully got reply from docMeta module")
                return True, (metaDict.get("modified_date"), title[:254], lang.src)
            
        except Exception as e:
            
            logger.error(e)
            logger.error("Did not get reply from docMeta module")
            if "JSON" in str(e):
                return False, "This kind of file can not be read"
            else:
                return False, "problem to fetch title and date of document"


    # def thumbnail_fun(self, source):

        logger = appLogger.get_logger(str(self.id))
        logger.info(f"DocumentsId:- {self.id} Started preocessing for thumbnail module")
        try:
            
            img_path = BASE_DIR + f"/files/{self.id}/"
            
            doc = self.doc
            page = doc.loadPage(0)
            pix = page.get_pixmap()
            output = img_path + f"{self.id}.jpg"
            pix.save(output)
            
            if not os.path.exists(img_path):
                logger.error("Directory doesn't exists for thumbfile")

            img = Image.open(BASE_DIR + f"/files/{self.id}/{self.id}.jpg")
            
            s3 = S3Events()
            s3_url = s3.process_and_upload(f'{source}/', img, str(self.id))
            img.close() 

            logger.info(f"DocumentsId:- {self.id} Successfully got reply from thumbnail module")
            return True, s3_url

        except Exception as e:

            logger.error(e)
            logger.error("Did not get reply from thumbnail module")
            return False, "problem to create thumbnail of document"


    def keywords_fun(self, gen):
        
        import yake
        try:
            from pyate import combo_basic
            
            doc = self.doc
            keyword_string = translation_fun(doc)
                
            keywordDict = dict(combo_basic(keyword_string).sort_values(ascending=False))
            if len(keywordDict):

                logger.info(f"DocumentsId:- {self.id} Successfully got reply from keywords module")
                return True, keywordDict
        
            else:
                
                yake_list = []
                for page in doc:
                    pdf_text = page.getText("text")
                    yake_list.append(pdf_text.replace("\n", ""))

                keyword_string = ""
                for y in yake_list:
                    keyword_string += y

                custom_kw_extractor = yake.KeywordExtractor(n = 3, dedupLim = 0.3, top = 30)
                yake_keywords = custom_kw_extractor.extract_keywords(keyword_string)

                logger.info(f"DocumentsId:- {id} Successfully got reply from keywords module")
                return True, yake_keywords[:30]
        
        except Exception as e:

            logger.error(e)
            logger.error("Did not get reply from keywords module")
            return False, "problem to fetch keywords of document"


    # def translation_fun(self):

        from googletrans import Translator

        try:
            translator = Translator()

            # using pymmupdf
            trans_list = []
            doc = self.doc
            for page in doc:
                pdf_text = page.getText("text")
                proText = pdf_text.replace("\n","").replace("-","").replace("_","").lower()
                chunks = [proText[t:t + 4500] for t in range(0, len(proText), 4500)]
                for i_chunk in range(len(chunks)):
                    trans_list.append((translator.translate(chunks[i_chunk], dest = 'en').text))

            keyword_string = ""
            for s in trans_list:
                keyword_string += s
                
            logger.info("Successfully got reply from translate module")
            return True, trans_list

        except Exception as e:

            logger.error(e)
            logger.error("Did not get reply from translate module")
            return False, "problem to translate document"


    # def summary_fun(self):
        
        import gc
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        logger = appLogger.get_logger(str(self.id))
        logger.info(f"DocumentsId:- {self.id} Started preocessing for summary module")
        
        try:
            doc = self.doc
            sum_strings = translation_fun(doc)
            doc.close()
            
            # resList = []
            # summarizer = pipeline('summarization')
            # for sumstring in sum_strings:
            #     summary = summarizer(sumstring, max_length = 37, min_length = 10, do_sample = False)
            #     resList.append(summary[0].get("summary_text"))
            
            # res = "".join(resList)
            str_process = text_preprocessing(sum_strings)
            
            model_name = "facebook/bart-large-xsum"
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
            
            # sum_list = []
            # for sum_string in sum_strings:
            batch = tokenizer(str_process, truncation=True, padding='longest', return_tensors="pt").to(device)
            translated = model.generate(**batch, 
                                        min_length = 100,
                                        max_length = 700,
                                        length_penalty = 2.0
            )
            sum_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
            
            # Release memory that is taken by CPU
            del(sum_strings)
            del(str_process)
            del(tokenizer)
            del(model)
            del(batch)
            del(translated)
            # del(sum_text)
                # sum_list.append(sum_text[0])
            gc.collect()
            # keyword_string = "".join(sum_list)
            
            logger.info(f"DocumentsId:- {self.id} Successfully got reply from summary module")
            
            return True, sum_text[0]
        
        except Exception as e:
            
            logger.error(e)
            logger.error("Did not get reply from summary module")
            return False, "problem to create summary of document"