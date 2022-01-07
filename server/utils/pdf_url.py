import os
import logging
import requests
from pipeline import BASE_DIR

logger = logging.getLogger(__name__)

lib_path = os.getenv('LIBRE_OFFICE_PATH')
metaDict = {}

def download_file(download_url, filename):
    try:
        r = requests.get(download_url, allow_redirects=True)
        file = open(filename, 'wb')
        file.write(r.content)
        file.close()
        logger.info("successfully downloaded document url")
        
        return dict(r.headers).get("Last-Modified","")

    except Exception as e:
        logger.error(e)
        logger.error("Check that document url is right or not")
        pass

def down_pdf_file(url, id, genVar):
    
    file_save_path = BASE_DIR + f"/files/{id}"
    extension = genVar.get('extension')
    file_path = BASE_DIR + f"/files/{id}/{id}.{extension}"
    
    mod_date = download_file(url, file_path)
        
    file_size = os.path.getsize(file_path)
    kb_file_size = format(file_size/1024.0, ".2f")
    metaDict.update({id : kb_file_size})
    
    metaDict.update({"modified_date" : mod_date})
    
    if extension != 'pdf':
        try:
            os.system(f"{lib_path} --convert-to pdf {file_path} --outdir {file_save_path}")
        except:
            print(f"There is an error for {extension} to pdf conversion")