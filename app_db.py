from sqlalchemy import MetaData, bindparam, create_engine
from sqlalchemy.schema import (Column, ForeignKeyConstraint,
                               PrimaryKeyConstraint, Table)
from sqlalchemy.sql import and_, insert, update
from sqlalchemy.types import DateTime, Float, Integer, String

from settings import DB_ENGINE_FILE, ECHO_DATABASE_INFO
from utils_log import getLogger
from collections import namedtuple

logger = getLogger('db')

# models


DB_ENGINE = create_engine('sqlite:///{}'.format(DB_ENGINE_FILE), echo=ECHO_DATABASE_INFO)

metadata = MetaData()

posts = Table(
    'posts',
    metadata,
    Column('blockid', String, nullable=False, comment='板块id'),
    Column('postid', Integer, nullable=False, comment='帖子id'),
    Column('title', String, nullable=False, comment='帖子标题'),
    Column('pageurl', String, nullable=False, comment='帖子首页url'),
    Column('subType', String, comment='帖子子类型'),
    Column('activityuserid', Integer, nullable=False, comment='楼主id'),
    Column('clickcount', Integer, nullable=False, comment='点击数'),
    Column('replycount', Integer, nullable=False, comment='回复数'),
    Column('remarkcount', Integer, nullable=False, comment='楼主发言数'),
    Column('imgcount', Integer, nullable=False, comment='图片数'),
    Column('posttime', DateTime, nullable=False, comment='主贴发帖时间'),
    PrimaryKeyConstraint('blockid', 'postid', name='post_pk')
)


replys = Table(
    'replys',
    metadata,
    Column('blockid', String, nullable=False, comment='板块id'),
    Column('postid', Integer, nullable=False, comment='帖子id'),
    Column('replyid', Integer, nullable=False, comment='回复id'),
    Column('hostid', Integer, nullable=False, comment='层主id'),
    Column('posttime', DateTime, nullable=False, comment='发布时间'),
    Column('content', String, default="", comment='内容'),
    Column('upCount', Integer, default=0, comment='点赞数'),
    Column('shang', Float, default=0, comment='打赏'),
    Column('totalScore', Float, default=0, comment='总天涯分'),
    Column('score', Float, default=0, comment='已获天涯分'),
    Column('estimateValue', Float, default=0, comment='预估天涯分'),
    PrimaryKeyConstraint('blockid', 'postid', 'replyid', name='reply_pk'),
    ForeignKeyConstraint(['blockid', 'postid'], ['posts.blockid', 'posts.postid'], name="blockid_postid_fk")
)


upusers = Table(
    'upusers',
    metadata,
    Column('blockid', String, nullable=False, comment='板块id'),
    Column('postid', Integer, nullable=False, comment='帖子id'),
    Column('replyid', Integer, nullable=False, comment='回复id'),
    Column('doUserId', Integer, nullable=False, comment='点赞的人的id'),
    ForeignKeyConstraint(
        ['blockid', 'postid', 'replyid'],
        ['replys.blockid', 'replys.postid', 'replys.replyid'],
        name="blockid_postid_replyid_fk"
    )
)

shangusers = Table(
    'shangusers',
    metadata,
    Column('blockid', String, nullable=False, comment='板块id'),
    Column('postid', Integer, nullable=False, comment='帖子id'),
    Column('doUserId', Integer, nullable=False, comment='打赏的人的id'),
    Column('shang', Float, nullable=False, comment='打赏数额'),
    ForeignKeyConstraint(
        ['blockid', 'postid'],
        ['posts.blockid', 'posts.postid'],
        name="blockid_postid_fk"
    )
)


Post = namedtuple('Post', [
    'blockid',
    'postid',
    'title',
    'pageurl',
    'subType',
    'activityuserid',
    'clickcount',
    'replycount',
    'remarkcount',
    'imgcount',
    'posttime'
])

Reply = namedtuple('Reply', [
    'blockid',
    'postid',
    'replyid',
    'hostid',
    'posttime',
    'content'
    # 'upCount',
    # 'shang',
    # 'totalScore',
    # 'score',
    # 'estimateValue'
])


metadata.create_all(DB_ENGINE)

# utils


class DB_Failed(BaseException):
    pass

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
