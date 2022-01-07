import gc
from .pdf_url import *
from pipeline import BASE_DIR
from .all_modules import Modules

def main_fun(url, gen, id, modules, source, timestamp):

    pdf = BASE_DIR + f"/files/{id}/{id}.pdf"

    my_res_dict = {}

    my_res_dict["url"] = url
    my_res_dict["id"] = id
    my_res_dict["timestamp"] = timestamp
    my_res_dict["general"] = gen
    
    moduleObj = Modules(pdf, id)
    
    for mod in modules:
        if mod == 'fileStats':
            fileStatFlag, fileStatRes = moduleObj.fileStats_fun()
            if fileStatFlag:
                my_res_dict.update({"fileStats" : {"pages": fileStatRes[0], "fileSize": fileStatRes[1]}})
            else:
                my_res_dict.update({"message" : fileStatRes})

        # elif mod == 'docMeta':
            docMetaFlag, docMetaRes = moduleObj.docMeta_fun()
            if docMetaFlag:
                my_res_dict.update({"docMeta" : {"date" : docMetaRes[0], "title" : docMetaRes[1], "language" : docMetaRes[2]}})
            else:
                my_res_dict.update({"message" : docMetaRes})
            
        # elif mod == 'thumbnail':
            thumbnailFlag, thumbnailRes = moduleObj.thumbnail_fun(source)
            if thumbnailFlag:
                my_res_dict.update({"thumbnail" : {"url" : thumbnailRes}})
            else:
                my_res_dict.update({"message" : thumbnailRes})
            
        elif mod == 'keywords':
            keywordFlag, keywordRes = moduleObj.keywords_fun(gen)
            if keywordFlag:
                my_res_dict.update({"keywords" : {"list" : keywordRes}})
            else:
                my_res_dict.update({"message" : keywordRes})
            garbageCollect = gc.collect()
            
        # elif mod == 'translate':
            translateFlag, translateRes = moduleObj.translation_fun()
            if translateFlag: 
                my_res_dict.update({"translated_string" : translateRes})
            else:
                my_res_dict.update({"message" : translateRes})
                
        # elif mod == 'summary':
            summaryFlag, summaryRes = moduleObj.summary_fun()
            if summaryFlag:
                my_res_dict.update({"summary" : summaryRes})
            else:
                my_res_dict.update({"summary" : summaryRes})
            garbageCollect = gc.collect()
            torch.cuda.empty_cache()
                
    return my_res_dict