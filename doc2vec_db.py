import pickle
from app_db import DB_ENGINE, rawcontents
from gensim.models.doc2vec import Doc2Vec

from sqlalchemy import update
from utils_log import getLogger

logger = getLogger('d2v_dump')

model = Doc2Vec.load('RuntimeTY/d2v_2048_5_1216')

logger.warning('Model Loaded')


with DB_ENGINE.connect() as conn:

    stmt = 'SELECT rid, content FROM rawcontents where rid > 1582112'

    pool = []

    for (rid, content) in conn.execute(stmt):
        pool.append((rid, pickle.dumps(model.infer_vector(content))))

        if rid % 0x10 == 0:
            transcation = conn.begin()
            try:
                for (rid, vector) in pool:
                    conn.execute(
                        update(rawcontents)
                        .where(rawcontents.c.rid == rid)
                        .values(vector=vector)
                    )

                transcation.commit()
            except:
                transcation.rollback()
                logger.critical('{} dump failed'.format(rid))
                raise
            else:
                logger.info('{} dump success'.format(rid))
                pool = []

        if rid % 0x1000 == 0:
            logger.warning('{} handling'.format(rid))

    if len(pool) != 0:
        transcation = conn.begin()
        try:
            for (rid, vector) in pool:
                conn.execute(
                    update(rawcontents)
                    .where(rawcontents.c.rid == rid)
                    .values(vector=vector)
                )

            transcation.commit()
        except:
            transcation.rollback()
            logger.critical('dump failed')
            raise
        else:
            logger.info('dump success')
            pool = []