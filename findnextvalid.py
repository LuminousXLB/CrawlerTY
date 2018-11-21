from pyperclip import copy
from crawler import urlFactory, session


blockid = 'worldlook'


def next(pid):
    pid += 1
    rsp = session.get(urlFactory(blockid, pid, 1))
    while rsp.status_code == 404:
        pid += 1
        rsp = session.get(urlFactory(blockid, pid, 1))
    copy(rsp.url)
    return pid, rsp
