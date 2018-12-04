from utils_log import getLogger, logging
from utils_request import fetchJson, with_max_retries
import json

logger = getLogger('reward', logging.INFO)


class FetchRewardInfoFailed(BaseException):
    pass


# app


def fetchRewardInfo(bbsGlobal):
    form = {
        'method': 'bbs.api.getArticleDashangInfo',
        'params.item': bbsGlobal['item'],
        'params.articleId': bbsGlobal['artId'],
    }

    for kform, kglob in {
        'params.rewardIds': 'tyfen_rewardIds',
        'params.tyfIds': 'tyfen_tyfIds',
        'params.shangIds': 'shangIds'
    }.items():
        if len(bbsGlobal[kglob]) > 0 and bbsGlobal[kglob][0] == '0':
            form[kform] = bbsGlobal[kglob]
        else:
            form[kform] = '0,' + bbsGlobal[kglob]

    rjson, _ = postReward('http://bbs.tianya.cn/api', form)

    ret = {}

    for key in ['tyf', 'shang', 'reward']:
        data = rjson['data'].get(key)
        ret[key] = [splitMerNum(item) for item in data] if data else []

    return ret

# utils


@with_max_retries(3, 0.5)
def postReward(url, form):
    rjson, rsp = fetchJson('http://bbs.tianya.cn/api', form)

    if 'error_msg' in rjson:
        raise FetchRewardInfoFailed(('post', form, rjson))

    return rjson, rsp


def splitMerNum(item):
    lst = item['merNum'].split('-')
    if len(lst) == 2:
        lst += [0]

    if len(lst) == 3:
        item['merNum'] = lst
        return item
    else:
        raise FetchRewardInfoFailed(('merNum', item))
