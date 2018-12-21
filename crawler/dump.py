from model.db import posts, replys, upusers, shangusers
from sqlalchemy.sql import and_, insert, update
from sqlalchemy import bindparam


# INSERT


def inserts(connection, table, data_list):
    return connection.execute(insert(table), data_list)


def insertPosts(connection, post_list):
    try:
        return inserts(connection, posts, post_list)
    except:
        raise  # DB_Failed(('insertPosts', post_list))


def insertReplys(connection, reply_list):
    try:
        return inserts(connection, replys, reply_list)
    except:
        raise  # DB_Failed(('insertReplys', reply_list))


def insertUpusers(connection, upusers_list):
    try:
        return inserts(connection, upusers, upusers_list)
    except:
        raise  # DB_Failed(('insertUpusers', upusers_list))


def insertShangusers(connection, shangusers_list):
    try:
        return inserts(connection, shangusers, shangusers_list)
    except:
        raise  # DB_Failed(('insertShangusers', shangusers_list))

# UPDATE


def updates(connection, stmt, data_list):
    # return [
    #     connection.execute(stmt.where(and_(
    #         replys.c.blockid == bindparam('blockid'),
    #         replys.c.postid == bindparam('postid'),
    #         replys.c.replyid == bindparam('replyid'),
    #     )), data) for data in data_list
    # ]
    return connection.execute(stmt.where(and_(
        replys.c.blockid == bindparam('pk_blockid'),
        replys.c.postid == bindparam('pk_postid'),
        replys.c.replyid == bindparam('pk_replyid'),
    )), data_list)


def updateReward(connection, reward_list):
    try:
        return updates(connection, update(replys).values(
            totalScore=bindparam('totalScore'),
            score=bindparam('score'),
            estimateValue=bindparam('estimateValue')
        ), reward_list)
    except:
        raise  # DB_Failed(('updateReward', reward_list))


def updateTyf(connection, tyf_list):
    try:
        return updates(connection, update(replys).values(
            upCount=bindparam('upCount'),
        ), tyf_list)
    except:
        raise  # DB_Failed(('updateTyf', tyf_list))


def updateShang(connection, shang_list):
    try:
        return updates(connection, update(replys).values(
            shang=bindparam('shang'),
        ), shang_list)
    except:
        raise  # DB_Failed(('updateShang', shang_list))
