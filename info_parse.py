import logging
import re
from urllib import parse

import demjson

from utils_datetime import parseDatetimeString
from utils_log import getLogger
from utils_request import getSoup, with_max_retries

logger = getLogger('parser', logging.INFO)


class FetchPostFailed(BaseException):
    pass


# app


def extractAll(blockid, postid):
    url = urlFactory(blockid, postid, 1)
    soup = getPage(url)
    if soup == None:
        return None

    bbsGlobal = extractBBSGlobal(soup)
    if bbsGlobal['isWenda'] or bbsGlobal['subType'] == '本版隐藏':
        logger.info('Got subtype with {} in {}'.format(bbsGlobal['subType'], url))
        return None

    post, masterReply = extractPost(soup, bbsGlobal)
    replys = [masterReply] + extractReplys(soup, bbsGlobal, skip_first=True)

    page = int(bbsGlobal['page'])
    pageCount = int(bbsGlobal['pageCount'])

    while page < pageCount:
        url = urlFactory(blockid, postid, page+1)
        soup = getPage(url)
        if soup == None:
            logger.warning('Got nothing from {} with page {}/{}'.format(url, page, pageCount))
            break

        bbsGlobal = extractBBSGlobal(soup)
        replys += extractReplys(soup, bbsGlobal, skip_first=False)
        page = int(bbsGlobal['page'])
        pageCount = int(bbsGlobal['pageCount'])

    return bbsGlobal, post, replys

# utils

# requests


def urlFactory(blockid, postid, page):
    return 'http://bbs.tianya.cn/post-{}-{}-{}.shtml'.format(blockid, postid, page)


@with_max_retries(3, 1)
def getPage(url):
    soup, rsp = getSoup(url)

    if rsp.status_code == 404:
        logger.info('Return {} from {} {}'.format(rsp.status_code, rsp.request.method, rsp.url))
        return None

    err = soup.find('div', {'id': 'main', 'class': 'error'})
    if err:
        raise FetchPostFailed((err.find('h2').text, rsp.url))

    return soup


# bbsGlobal


def extractBBSGlobal(soup):
    for script in soup.findAll('script'):
        if script.text.find('bbsGlobal') > -1:
            reg = re.compile(r'var adsGlobal [\s\S]*', re.M)
            bbsGlobal = re.sub(reg, '', script.text).replace('var bbsGlobal =', '').replace(';', '').strip()
            return demjson.decode(bbsGlobal)


# posts
# posts = (
#     'blockid',          # #post_head.atl-menu
#     'postid',           # #post_head.atl-menu
#     'pageurl',          # #post_head.atl-menu
#     'title',            # #post_head.atl-menu
#     'activityuserid',   # #post_head.atl-menu
#     'clickcount',       # #post_head.atl-menu
#     'replycount',       # #post_head.atl-menu
#     'posttime'          # #post_head.atl-info
#     'subType',          # bbsGlobal
#     'remarkcount',      # .host-data
#     'imgcount',         # .host-data
# )


def extractPost(bbsGlobal, soup):
    post = {}

    post_head = soup.find('div', id='post_head')
    post.update(parseAtlMenu(post_head.find('div', {'class': 'atl-menu'})))
    post.update(parseAtlMenu(post_head.find('div', {'class': 'atl-info'})))

    post['subType'] = bbsGlobal['subType']

    host_item = soup.find('div', {'class': 'host-item'})
    post.update(parseHostData(host_item.find('div', {'class': 'host-data'})))

    masterReply = extractMasterReply(bbsGlobal, host_item, post['posttime'])

    return post, masterReply


def parseAtlMenu(atl_menu):
    post = {}

    for kpost, katl in {
        'blockid': 'js_blockid',                                # 板块id
        'pageurl': 'js_pageurl',                                # 帖子url
        'postid': 'js_postid',                                  # 帖子id
        'activityuserid': 'js_activityuserid',                  # 楼主id
        'replycount': 'js_replycount',                          # 回复数
        'clickcount': 'js_clickcount'                           # 点击数
    }.items():
        post[kpost] = atl_menu.get(katl)

    post['title'] = parse.unquote(atl_menu.get('js_title')).strip()

    return post


def parseAtlInfo(atl_info):
    dts = atl_info.findAll('span')[1].text.replace('时间：', '').strip()

    post = {}
    post['posttime'] = parseDatetimeString(dts)                 # 发帖时间

    return post


def parseHostData(host_data):
    reg = re.compile(r'楼主发言：(\d+)次 发图：(\d+)张')

    post = {}
    matobj = reg.match(host_data.text.strip()).groups()       # 楼主发言数、发图片数
    post['remarkcount'], post['imgcount'] = matobj

    return post


def extractMasterReply(bbsGlobal, host_item, posttime):
    return {
        'blockid': bbsGlobal['item'],
        'postid': bbsGlobal['artId'],
        'replyid': 0,
        'hostid': host_item.get('_hostid'),
        'posttime': posttime,
        'content': host_item.find('div', {'class': 'bbs-content'}).prettify()
    }


# replys
# replys = (
#     'blockid',    'postid',
#     'replyid',    'hostid',   'posttime',     'content',
#     'upCount',    'shang',    'totalScore',   'score',    'estimateValue'
# )

def extractReplys(soup, bbsGlobal, skip_first=False):
    atl_item_iter = iter(soup.findAll('div', {'class': 'atl-item'}))
    replys = []

    if skip_first:
        next(atl_item_iter)

    for atl_item in atl_item_iter:
        replys.append({
            'blockid': bbsGlobal['item'],
            'postid': bbsGlobal['artId']
        }.update(parseReplyItem(atl_item)))

    return replys


def parseReplyItem(atl_item):
    reply = {}

    for krly, katl in {
        'replyid': 'replyid',                                   # 回复id
        'hostid': '_hostid',                                    # 回复用户的id
        'posttime': 'js_restime'                                # 回复时间
    }.items():
        reply[krly] = atl_item.get(katl)

    content = atl_item.find('div', {'class': 'bbs-content'})
    reply['content'] = content.prettify()     # 回复内容

    return reply
