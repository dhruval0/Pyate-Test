import logging

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

def get_file_handler(id):
    # file_handler = logging.FileHandler(f"/home/administrator/ai-dev/fastapiLog/{id}.log")
    file_handler = logging.FileHandler(f"D:/Final_pro/fastapiLog/{id}.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_logger(id):
    logger = logging.getLogger(id)
    logger.setLevel(logging.INFO)
    for hdlr in logger.handlers[:]:
        if isinstance(hdlr, logging.FileHandler):
            logger.removeHandler(hdlr)
    logger.addHandler(get_file_handler(id))
    return logger