import json
import logging

from info_parse import extractAll
from info_reward import fetchRewardInfo
from settings import DATA_ROOT
from app_db import (DB_ENGINE, insertPosts, insertReplys, updateReward,
                    updateShang, updateTyf)
from utils_log import getLogger
from utils_request import with_max_retries

logger = getLogger('handle', logging.INFO)


def handlePost(blockid, postid):
    name = 'post-{}-{}'.format(blockid, postid)
    info = fetchinfo(blockid, postid, name)
    if info is None:
        return

    post, replys, rewards, bbsGlobal = info
    dumpinfo(post, replys, rewards, bbsGlobal, name)


@with_max_retries(3, 60)
def fetchinfo(blockid, postid, name):
    logger.info('Handling {}'.format(name))

    ext = extractAll(blockid, postid)
    if ext is None:
        logger.info('Handling suspended with {}'.format(name))
        return

    bbsGlobal, post, replys = ext
    rewards = fetchRewardInfo(bbsGlobal)

    return post, replys, rewards, bbsGlobal


def dumpinfo(post, replys, rewards, bbsGlobal, name):
    # dump bbsGlobal
    fn = DATA_ROOT/'{}.json'.format(name)

    with open(str(fn), "w", encoding="utf-8") as f:
        f.write(json.dumps(bbsGlobal, ensure_ascii=False))

    logger.info('Dump bbsGlobal {} success'.format(name))

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

            transcation.commit()
        except:
            logger.critical('Persistant {} failed'.format(name))
            transcation.rollback()
            raise
        else:
            logger.info('Persistant {} success'.format(name))
