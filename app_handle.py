import json
import logging

from info_parse import extractAll
from info_reward import fetchRewardInfo
from settings import DATA_ROOT
from utils_db import (DB_ENGINE, insertPosts, insertReplys, updateReward,
                      updateShang, updateTyf)
from utils_log import getLogger

logger = getLogger('handle', logging.INFO)


def handlePost(blockid, postid):
    name = 'post-{}-{}'.format(blockid, postid)
    logger.info('Handling {}'.format(name))

    bbsGlobal, posts, replys = extractAll(blockid, postid)
    [tyf, shang, reward] = fetchRewardInfo(bbsGlobal)

    # persistant
    with DB_ENGINE.connect() as connection:
        transcation = connection.begin()
        try:
            insertPosts(connection, posts)
            insertReplys(connection, replys)
            updateTyf(connection, tyf)
            updateShang(connection, shang)
            updateReward(connection, reward)
            transcation.commit()
        except:
            logger.critical('Persistant {} failed'.format(name))
            transcation.rollback()
            raise
        else:
            logger.info('Persistant {} success'.format(name))

    # dump bbsGlobal
    fn = DATA_ROOT/name+'.json'
    json.dump(bbsGlobal, fn.open(), ensure_ascii=False)
