import os
import json
import shutil
import logging
import requests
import logging.config
from .models import Item
from .utils.pdf_url import *
from pipeline import BASE_DIR
from dotenv import load_dotenv
from server.utils import appLogger
from .dependencies import get_token_header
from .utils.pdf_title_date import main_fun
from fastapi.encoders import jsonable_encoder
from fastapi import BackgroundTasks, Depends, FastAPI

load_dotenv()

log_path = os.getenv('LOG_PATH')
digital_brain_auth_token = os.getenv('DIGITAL_BRAIN_AUTH_TOKEN')

app = FastAPI()
logging.basicConfig(level=logging.INFO,
                    format="{asctime} {name} {lineno} {levelname:<8} {message}",
                    style='{',
                    filename=f"{log_path}",
                    filemode='a',
                    )

logger = logging.getLogger(__name__)


@app.get("/")
def orchtel_home():
    return {"Welcome to": "Test AI"}


@app.post("/process-document/v1", dependencies=[Depends(get_token_header)])
async def process_document(item: Item, background_tasks: BackgroundTasks):

    payload = jsonable_encoder(item)
    end_point = payload["callBackUrl"]

    if end_point:
        background_tasks.add_task(execute_in_background, item)
        return {"message": "Task is running in the background"}
    else:
        docs = process_documents(payload)
        logger.info("Successfully processed pyaload")
        return {"documents": docs}


def execute_in_background(item: Item):
    payload = jsonable_encoder(item)

    docs = process_documents(payload)

    end_point = payload["callBackUrl"]
    res_dict = {"documents": jsonable_encoder(docs)}
    docId = res_dict.get("documents")[0].get("id")
    logger = appLogger.get_logger(str(docId))
    r = requests.post(end_point,
                      data=json.dumps(res_dict),
                      headers={
                          "Content-Type": "application/json",
                          "Accept": "application/json"
                      })

def process_documents(payload):

    res = []
    doc = payload["documents"]

    for data in range(len(doc)):
        url_var = doc[data]["url"]
        sour_var = doc[data]["source"]
        id_var = doc[data]["id"]
        timestamp_var = doc[data]["timestamp"]
        mod_var = doc[data]["modules"]

        logger = appLogger.get_logger(str(id_var))

        logger.info(
            "=====================================================================")
        logger.info("requestID:-" + f"{id_var}" + " url:-" + f"{url_var}")
        logger.info(
            "=====================================================================")

        dir_path = BASE_DIR + f"/files/{id_var}"
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        genVar = {}
        url_res = requests.get(url_var)
        mimetype = dict(url_res.headers).get("Content-Type")
        
        if not mimetype:
            mimetype = dict(url_res.headers).get("content-type")

        genVar.update({"valid": False})
        if ((url_res.status_code == 200)) & (("application/pdf" in mimetype) | ("word" in mimetype) | ("excel" in mimetype)):
            genVar.update({"valid": True})
        elif (url_res.status_code == 404) | ("text/html" in mimetype) | ("zip" in url_var):
            genVar.update({"valid": False})

        extension = url_var.split("/")[-1].split(".")[1][0:3]
        genVar.update({"extension": extension})

        genVar.update({"mimeType": mimetype.split(';')[0]})

        genVar.update({"gpuMemoryOverflow": False})
        genVar.update({"cpuUtilizationOveflow": False})

        if (str(genVar.get("valid")) == "True") & (str(genVar.get("cpuUtilizationOveflow")) == "False"):
            down_pdf_file(url_var, id_var, genVar)
            var = main_fun(url_var, genVar, id_var,
                           mod_var, sour_var, timestamp_var)

        else:
            false_var = {}
            false_var.update({"id": id_var})
            false_var.update({"url": url_var})
            false_var.update({"timestamp": timestamp_var})
            false_var.update({"general": genVar})
            var = false_var

        res.append(var)

        # For deleting file after execution
        shutil.rmtree(BASE_DIR + f"/files/{id_var}")

    return res
