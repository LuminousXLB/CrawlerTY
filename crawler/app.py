import json
import logging

from crawler.dump import (insertPosts, insertReplys, insertShangusers,
                          insertUpusers, updateReward, updateShang, updateTyf)
from crawler.mainpart import extractAll
from crawler.reward import fetchRewardInfo
from crawler.upuser import fetchUpuserInfo
from model.db import DB_ENGINE
from settings import DATA_ROOT
from utils.log import getLogger
from utils.request import with_max_retries

logger = getLogger('handle', logging.INFO)


def handlePost(blockid, postid):
    name = 'post-{}-{}'.format(blockid, postid)
    info = fetchinfo(blockid, postid, name)
    if info is None:
        return

    post, replys, rewards, upUsers, shangUsers, GlobalList = info
    dumpinfo(post, replys, rewards, upUsers, shangUsers, GlobalList, name)


@with_max_retries(3, 60)
def fetchinfo(blockid, postid, name):
    logger.info('Handling {}'.format(name))

    ext = extractAll(blockid, postid)
    if ext is None:
        logger.info('Handling suspended with {}'.format(name))
        return

    GlobalList, post, replys = ext
    for bbsGlobal in GlobalList:
        rewards, merNumList = fetchRewardInfo(bbsGlobal)

    upUsers = fetchUpuserInfo(merNumList)

    shangUsers = []

    dashang = GlobalList[0].get('dashang')
    if dashang is not None:
        newestRecords = dashang.get('newestRecords')
        if newestRecords is not None:
            for record in newestRecords:
                shangUsers.append({
                    'blockid': blockid,
                    'postid': postid,
                    'doUserId': record['doUserId'],
                    'shang': record['shang']
                })

    return post, replys, rewards, upUsers, shangUsers, GlobalList


def dumpinfo(post, replys, rewards, upUsers, shangUsers, GlobalList, name):
    # dump GlobalList
    fn = DATA_ROOT/'{}.json'.format(name)

    with open(str(fn), "w", encoding="utf-8") as f:
        f.write(json.dumps(GlobalList, ensure_ascii=False))

    logger.info('Dump GlobalList {} success'.format(name))

    # persistant
    with DB_ENGINE.connect() as connection:
        transcation = connection.begin()
        try:
            insertPosts(connection, [post])
            insertReplys(connection, replys)
            if len(rewards['tyf']) > 0:
                updateTyf(connection, rewards['tyf'])

            if len(rewards['shang']) > 0:
                updateShang(connection, rewards['shang'])

            if len(rewards['reward']) > 0:
                updateReward(connection, rewards['reward'])

            if len(upUsers) > 0:
                insertUpusers(connection, upUsers)

            if len(shangUsers) > 0:
                insertShangusers(connection, shangUsers)

            transcation.commit()
        except:
            logger.critical('Persistant {} failed'.format(name))
            transcation.rollback()
            raise
        else:
            logger.info('Persistant {} success'.format(name))
