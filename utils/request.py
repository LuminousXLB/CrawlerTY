import json
import logging
import time
from functools import wraps

import requests
from bs4 import BeautifulSoup

from utils.log import getLogger

logger = getLogger('request', logging.INFO)

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'

# functions


def lauchRequest(req_func, ret_func, sleep_time):
    def func(*args, sleep_time=sleep_time):
        time.sleep(sleep_time)
        rsp = req_func(*args)

        logger.debug('Return {} from {} {}'.format(rsp.status_code, rsp.request.method, rsp.url))

        return ret_func(rsp), rsp

    return func


getSoup = lauchRequest(
    lambda url: session.get(url),
    lambda rsp: BeautifulSoup(rsp.content, 'lxml'),
    sleep_time=0.1
)

fetchJson = lauchRequest(
    lambda url, form: session.post(url, form),
    lambda rsp: json.loads(rsp.text),
    sleep_time=0
)

getJson = lauchRequest(
    lambda url: session.get(url),
    lambda rsp: json.loads(rsp.text),
    sleep_time=0
)

# utils


def with_max_retries(count, sleep):
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(count):
                try:
                    ret = func(*args, **kwargs)
                except Exception as e:
                    logger.info('try %s: %r failed with %r', i, func, e)
                    if i == count - 1:
                        raise e
                    else:
                        time.sleep(sleep)
                else:
                    return ret
        return wrapper
    return real_decorator
