import json
import logging

from info_parse import extractAll
from info_reward import fetchRewardInfo
from settings import DATA_ROOT
from app_db import (DB_ENGINE, insertPosts, insertReplys, updateReward,
                    updateShang, updateTyf)
from utils_log import getLogger

logger = getLogger('handle', logging.INFO)


def handlePost(blockid, postid):
    name = 'post-{}-{}'.format(blockid, postid)
    logger.info('Handling {}'.format(name))

    bbsGlobal, post, replys = extractAll(blockid, postid)
    rewards = fetchRewardInfo(bbsGlobal)

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

    # dump bbsGlobal
    fn = DATA_ROOT/'{}.json'.format(name)

    with open(str(fn), "w", encoding="utf-8") as f:
        f.write(json.dumps(bbsGlobal, ensure_ascii=False))

    logger.info('Dump bbsGlobal {} success'.format(name))
