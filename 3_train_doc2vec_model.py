from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import common_texts
from sqlalchemy import select

from model.db import DB_ENGINE, posts, rawcontents
from utils.log import getLogger

logger = getLogger('doc2vec')

# init

with DB_ENGINE.connect() as conn:
    s = select([posts.c.title])
    documents = [TaggedDocument(doc, [pid])
                 for pid, doc in enumerate(conn.execute(s))]

model = Doc2Vec(documents, vector_size=2048, window=5, min_count=1, workers=4)


model.save('RuntimeTY/d2v_2048_5_1216')

model = Doc2Vec.load('RuntimeTY/d2v_2048_5_1216')

logger.critical('Loaded')

with DB_ENGINE.connect() as conn:
    s = select([rawcontents])
    buffer = []

    for row in conn.execute(s):
        rid = row[rawcontents.c.rid]
        content = row[rawcontents.c.content]
        buffer.append(TaggedDocument(content, [rid]))

        if len(buffer) >= 0x10:
            try:
                model.train(buffer, total_examples=len(buffer), epochs=model.epochs)

                if rid % 0x100 == 0:
                    logger.critical('train@{}'.format(rid))
                    if rid % 0x10000 == 0:
                        model.save('RuntimeTY/d2v_2048_5_1216')
                        logger.critical('save@{}'.format(rid))

                buffer = []
            except KeyboardInterrupt:
                logger.critical('KeyboardInterrupt@{}'.format(rid))
                raise

    if len(buffer) != 0:
        model.train(buffer, total_examples=len(buffer), epochs=model.epochs)

    model.save('RuntimeTY/d2v_2048_5_1216')
