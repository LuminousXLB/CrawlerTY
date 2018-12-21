from utils.log import getLogger, logging
from utils.request import fetchJson, with_max_retries
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
    merNumList = set()

    for key in ['tyf', 'shang', 'reward']:
        data = rjson['data'].get(key)

        merNumList.update([item['merNum'] for item in data] if data else [])
        ret[key] = [splitMerNum(item) for item in data] if data else []

    return ret, list(merNumList)

# utils


@with_max_retries(3, 1)
def postReward(url, form):
    rjson, rsp = fetchJson('http://bbs.tianya.cn/api', form)

    assert(rsp.status_code == 200), 'Got {} during {} {}'.format(
        rsp.status_code, rsp.request.method, rsp.url
    )

    if not rjson.get('success'):
        raise FetchRewardInfoFailed(('post', form, rjson))

    return rjson, rsp


def splitMerNum(item):
    lst = item['merNum'].split('-')
    if len(lst) == 2:
        lst += [0]

    if len(lst) == 3:
        item['pk_blockid'] = lst[0]
        item['pk_postid'] = lst[1]
        item['pk_replyid'] = lst[2]
        return item
    else:
        raise FetchRewardInfoFailed(('merNum', item))
