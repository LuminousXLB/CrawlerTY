from pathlib import Path
import json
from settings import DATA_ROOT
from models import DB_ENGINE, posts, replys
from utils import getLogger

logger = getLogger('db')


def loadJson(path):
    logger.info('Load {}'.format(path))
    path = path if isinstance(path, Path) else Path(path)
    with path.open() as f:
        return json.load(f)


def cleanPostItem(post):
    for key in ['postid', 'activityuserid', 'replycount', 'clickcount', 'remarkcount', 'imgcount']:
        post[key] = int(post[key])

    post['posttime'] = parse_dt(post['posttime'])

    return post


def cleanReplyItem(item):
    for key in ['replyid', 'hostid', 'length']:
        item[key] = int(item[key])

    if not item.get('upCount'):
        item['upCount'] = 0

    if not item.get('totalScore'):
        item['totalScore'] = .0

    item['resttime'] = parse_dt(item['resttime'])
    return item


def unify(post):
    pk = {
        'blockid': post['blockid'],
        'postid': int(post['postid'])
    }

    replys = post.pop('replys')
    for item in replys:
        item.update(pk)
        item = cleanReplyItem(item)

    return cleanPostItem(post), replys


def persistant(po, re):
    try:
        conn = DB_ENGINE.connect()
        conn.execute(posts.insert(), po)
        if len(re) > 0:
            conn.execute(replys.insert(), re)
    finally:
        conn.close()


def doit(path):
    jsondata = loadJson(path)
    po, re = unify(jsondata)
    persistant(po, re)
    logger.info('Bye {}'.format(path))


if __name__ == "__main__":
    from os import walk

    for root, dirs, files in walk(DATA_ROOT):
        logger.info('Hello {}'.format(root))
        for f in files:
            path = Path(root, f)
            if path.suffix == '.json':
                logger.info('Hello {}'.format(path))
                doit(path)
                logger.info('Bye {}'.format(path))
        logger.info('Hello {}'.format(root))
