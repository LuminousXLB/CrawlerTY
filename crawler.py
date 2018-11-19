import json
import logging
import re
import time
from collections import OrderedDict
from urllib import parse

import demjson
import requests
from bs4 import BeautifulSoup

from utils import getLogger

logger = getLogger('crawler', logging.INFO)
session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'


def getSoup(url):
    time.sleep(0.1)
    rsp = session.get(url)
    logger.info('return {} from {} {}'.format(rsp.status_code, rsp.request.method, rsp.url))
    if rsp.status_code == 200:
        return BeautifulSoup(rsp.content, 'lxml'), rsp
    else:
        return None, rsp


def urlFactory(blockid, postid, page):
    return 'http://bbs.tianya.cn/post-{}-{}-{}.shtml'.format(blockid, postid, page)


def fetchRewardInfo(bbsGlobal):

    form = {
        "method": "bbs.api.getArticleDashangInfo",
        "params.item": bbsGlobal['item'],
        "params.articleId": bbsGlobal['artId'],
        "params.rewardIds": bbsGlobal['tyfen_rewardIds'],
        "params.tyfIds": bbsGlobal['tyfen_tyfIds'],
        "params.shangIds": bbsGlobal['shangIds']
    }

    if bbsGlobal['tyfen_rewardIds'][0] != '0':
        form['params.rewardIds'] = '0,' + form['params.rewardIds']
        form['params.tyfIds'] = '0,' + form['params.tyfIds']

    rsp = session.post('http://bbs.tianya.cn/api', form)

    data = json.loads(rsp.text)['data']
    ret = {}

    for item in data['tyf']:
        ret[item['merNum']] = {'upCount': item['upCount']}

    for item in data['reward']:
        ret[item['merNum']]['totalScore'] = item['totalScore']

    return ret, rsp


def bbsContentLength(soup):
    return len(soup.find('div', {'class': 'bbs-content'}).prettify())


def parseBBSGlobal(script_list):
    for script in script_list:
        if script.text.find('bbsGlobal') > -1:
            reg = re.compile(r'var adsGlobal [\s\S]*', re.M)
            bbsGlobal = re.sub(reg, '', script.text).replace('var bbsGlobal =', '').replace(';', '').strip()
            return demjson.decode(bbsGlobal)


def parseHeader(post_head):
    meta = OrderedDict()

    atl_menu = post_head.find('div', {'class': 'atl-menu'})
    atl_info = post_head.find('div', {'class': 'atl-info'}).findAll('span')

    meta['blockid'] = atl_menu.get('js_blockid')                                # 板块id
    meta['pageurl'] = atl_menu.get('js_pageurl')                                # 帖子url
    meta['postid'] = atl_menu.get('js_postid')                                  # 帖子id
    meta['activityuserid'] = atl_menu.get('js_activityuserid')                  # 楼主id
    meta['posttime'] = atl_info[1].text.replace('时间：', '').strip()           # 发帖时间
    meta['posttimestamp'] = atl_menu.get('js_posttime')                         # 发帖时间戳
    meta['replycount'] = atl_menu.get('js_replycount')                          # 回复数
    meta['clickcount'] = atl_menu.get('js_clickcount')                          # 点击数

    logger.info('url_{} title_{} username_{}'.format(
        atl_menu.get('js_pageurl'),
        parse.unquote(atl_menu.get('js_title')),
        parse.unquote(atl_menu.get('js_activityusername'))
    ))

    return meta


def parseHostItem(atl_main):
    host_item = atl_main.find('div', {'class': 'host-item'})
    host_data = host_item.find('div', {'class': 'host-data'}).text.strip()
    reg = re.compile(r'楼主发言：(\d+)次 发图：(\d+)张')

    meta = OrderedDict()
    meta['length'] = bbsContentLength(host_item)                                # 主帖内容长度
    meta['remarkcount'], meta['imgcount'] = reg.match(host_data).groups()       # 楼主发言数、发图片数

    return meta


def parseReplyItem(atl_item):
    meta = OrderedDict()
    meta['replyid'] = atl_item.get('replyid')                                   # 回复id
    meta['hostid'] = atl_item.get('_hostid')                                    # 回复用户的id
    meta['resttime'] = atl_item.get('js_restime')                               # 回复时间
    meta['length'] = bbsContentLength(atl_item)                                 # 回复内容长度

    logger.debug('id_{} replyid_{} username_{}'.format(
        atl_item.get('id'),
        atl_item.get('replyid'),
        atl_item.get('js_username')
    ))

    return meta


def parseReplys(atl_item_iter, rewards, bbsGlobal):
    replys = []

    for atl_item in atl_item_iter:
        atl = parseReplyItem(atl_item)

        key = '-'.join([bbsGlobal['item'],
                        str(bbsGlobal['artId']), atl['replyid']])
        if rewards != None:
            reward = rewards.get(key) or {'upCount': '', 'totalScore': ''}
            atl.update(reward)

        replys.append(atl)

    return replys


def handleFirstPage(soup):
    bbsGlobal = parseBBSGlobal(soup.findAll('script'))
    logger.info('block_{item} article_{artId} page_{page}'.format_map(bbsGlobal))

    if bbsGlobal['isWenda'] or bbsGlobal['subType'] == '本版隐藏':
        return None, bbsGlobal
    else:
        meta = OrderedDict()

        # 解析主帖信息
        meta.update(parseHeader(soup.find('div', id='post_head')))
        meta.update(parseHostItem(soup.find('div', {'class': 'atl-main'})))
        meta['subType'] = bbsGlobal['subType']

        if bbsGlobal['tyfen_rewardIds'] != '':
            rewards, rsp = fetchRewardInfo(bbsGlobal)
            mainkey = '-'.join([meta['blockid'], meta['postid']])
            meta.update(rewards[mainkey])
        else:
            rewards = None

        # 解析回复信息
        atl_item_iter = iter(soup.findAll('div', {'class': 'atl-item'}))
        next(atl_item_iter)  # 跳过第一个
        meta['replys'] = parseReplys(atl_item_iter, rewards, bbsGlobal)
        return meta, bbsGlobal


def handleFollowingPage(soup):
    bbsGlobal = parseBBSGlobal(soup.findAll('script'))
    logger.info('block_{item} article_{artId} page_{page}'.format_map(bbsGlobal))

    if bbsGlobal['tyfen_rewardIds'] != '':
        rewards, rsp = fetchRewardInfo(bbsGlobal)
    else:
        rewards = None

    atl_item_iter = iter(soup.findAll('div', {'class': 'atl-item'}))

    return parseReplys(atl_item_iter, rewards, bbsGlobal)


def handlePost(blockid, postid):
    soup, rsp = getSoup(urlFactory(blockid, postid, 1))
    if soup == None:
        logger.warning('{} {} {}'.format(rsp.status_code, rsp.request.method, rsp.url))
        return None

    err = soup.find('div', {'id': 'main', 'class': 'error'})
    if err:
        logger.warning('Got error: {}'.format(err.find('h2').text))
        return None

    meta, bbsGlobal = handleFirstPage(soup)

    if meta == None:
        logger.warning('Got subtype with {}'.format(bbsGlobal['subType']))
        return None

    pageCount = bbsGlobal['pageCount']

    if pageCount != 1:
        for page in range(2, pageCount+1):
            soup, rsp = getSoup(urlFactory(blockid, postid, page))
            if rsp.status_code == 200:
                meta['replys'] += handleFollowingPage(soup)

    return meta
