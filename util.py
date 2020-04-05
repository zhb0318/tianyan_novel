import requests
import logging
import asyncio
from bs4 import BeautifulSoup
import time
from threading import Thread
import logging
from config import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('tianyan.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s  - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
logger.info('You can find this written in myLogs.log')


def get_proxy():
    url = "http://" + proxy_pool["IP"] + ":" + proxy_pool["Port"]
    proxy = requests.get(url + "/get/").json().get("proxy")
    if proxy:
        return {"http": "http://{}".format(proxy)}
    else:
        return None

    

def my_request(url, retry_time=5):
    i = 0
    while i < retry_time:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                return r.text
            else:
                raise Exception
        except:
            logger.info("Request Timeout, will retry later")
            i = i + 1
            time.sleep(30)
            if i == 4:
                logger.warning("多次尝试失败，休眠1024秒")
                time.sleep(1024)
    logger.error("Request Error, url:" + url)
