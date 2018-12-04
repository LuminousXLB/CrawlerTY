import logging

from info_parse import extractAll
from info_reward import fetchRewardInfo
from utils_db import (DB_ENGINE, insertPosts, insertReplys, updateReward,
                      updateShang, updateTyf)
from utils_log import getLogger

logger = getLogger('handle', logging.INFO)


def handlePost(blockid, postid):
    bbsGlobal, posts, replys = extractAll(blockid, postid)
    [tyf, shang, reward] = fetchRewardInfo(bbsGlobal)
    with DB_ENGINE.connect() as connection:
        transcation = connection.begin()
        try:
            insertPosts(connection, posts)
            insertReplys(connection, replys)
            updateTyf(connection, tyf)
            updateShang(connection, shang)
            updateReward(connection, reward)
        except:
            transcation.rollback()
        else:
            transcation.commit()
