from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import Table, Column, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.types import Integer, String, DateTime, Float
from settings import DB_ENGINE_FILE, ECHO_DATABASE_INFO

DB_ENGINE = create_engine('sqlite:///{}'.format(DB_ENGINE_FILE), echo=ECHO_DATABASE_INFO)

metadata = MetaData()

posts = Table('posts', metadata,
              Column('blockid', String, nullable=False, comment='板块id'),
              Column('postid', Integer, nullable=False, comment='帖子id'),
              Column('pageurl', String, nullable=False, comment='帖子首页url'),
              Column('subType', String, comment='帖子子类型'),
              Column('activityuserid', Integer, nullable=False, comment='楼主id'),
              Column('clickcount', Integer, nullable=False, comment='点击数'),
              Column('replycount', Integer, nullable=False, comment='回复数'),
              Column('remarkcount', Integer, nullable=False, comment='楼主发言数'),
              Column('imgcount', Integer, nullable=False, comment='图片数'),
              Column('posttime', DateTime, nullable=False, comment='主贴发帖时间'),
              Column('length', Integer, nullable=False, comment='主帖长度'),
              Column('upCount', Integer, comment='主贴点赞数'),
              Column('totalScore', Float, comment='主贴天涯分'),
              PrimaryKeyConstraint('blockid', 'postid', name='post_pk')
              )

replys = Table('replys', metadata,
               Column('blockid', String, nullable=False, comment='板块id'),
               Column('postid', Integer, nullable=False, comment='帖子id'),
               Column('replyid', Integer, nullable=False, comment='回复id'),
               Column('hostid', Integer, nullable=False, comment='层主id'),
               Column('resttime', DateTime, nullable=False, comment='回复时间'),
               Column('length', Integer, nullable=False, comment='回复长度'),
               Column('upCount', Integer, comment='回复点赞数'),
               Column('totalScore', Float, comment='回复天涯分'),
               ForeignKeyConstraint(['blockid', 'postid'], ['posts.blockid', 'posts.postid'], name="blockid_postid_fk")
               )


metadata.create_all(DB_ENGINE)
