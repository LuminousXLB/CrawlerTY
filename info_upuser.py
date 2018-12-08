from utils_log import getLogger, logging
from utils_request import getJson, with_max_retries
import json

logger = getLogger('Upuser', logging.INFO)


class FetchUpuserInfoFailed(BaseException):
    pass


# app


def fetchUpuserInfo(merNumList):
    ret = []

    for merNum in merNumList:
        [blockid, postid, replyid] = splitMerNum(merNum)
        rjson, _ = getUpuser(merNum)
        data = rjson['data'].get('list')
        if data is not None:
            for item in data:
                ret.append({
                    'blockid': blockid,
                    'postid': postid,
                    'replyid': replyid,
                    'doUserId': item['userId']
                })

    return ret

# utils


@with_max_retries(3, 0.5)
def getUpuser(merNum):
    rjson, rsp = getJson(
        'http://vote-tyt.tianya.cn/api/call.do?method=tyf.web.getUserListByMerNum&merId=1&merNum={}'.format(merNum)
    )

    assert(rsp.status_code == 200), 'Got {} during {} {}'.format(
        rsp.status_code, rsp.request.method, rsp.url
    )

    if not rjson.get('success'):
        raise FetchUpuserInfoFailed(('post', merNum, rjson))

    return rjson, rsp


def splitMerNum(merNum):
    lst = merNum.split('-')
    if len(lst) == 2:
        lst += [0]

    if len(lst) == 3:
        return lst
    else:
        raise FetchUpuserInfoFailed(('merNum', merNum))
