import langdetect
from googletrans import Translator

def translation_fun(doc):
    
    key_list = []
    translator = Translator()
    
    # Using Googletrans library
    for page in doc.pages(0, 29):
        pdf_text = page.getText("text")
        proText = pdf_text.replace("\n","").replace("-","").replace("_","").lower()
        chunks = [proText[t:t + 4500] for t in range(0, len(proText), 4500)]
        for i_chunk in range(len(chunks)):
            key_list.append((translator.translate(chunks[i_chunk], dest = 'en').text))

    keyword_string = "".join(key_list)
    return keyword_string