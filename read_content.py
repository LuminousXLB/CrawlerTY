# import json
from collections import Counter
# import jieba
# import random 
from bs4 import BeautifulSoup
from sqlalchemy import select

from app_db import DB_ENGINE, rawcontents, replys
from utils_log import getLogger
import pandas as pd

logger = getLogger('NLP')
counter = Counter()

# jieba.load_userdict('jieba_dict.txt')

rows = []
with DB_ENGINE.connect() as conn:
    s = select([replys.c.rid, replys.c.content]).where("replys.rid > 752958")
    # rows = conn.execute(s).fetchall()
    # rows = list(rows)
    # logger.info('database read completed')

    for row in conn.execute(s):
        rid = row[replys.c.rid]
        content = row[replys.c.content]
        try:

            if rid % 0x100 == 0:
                logger.info(rid)
                # if rid % 0x10000 == 0:
                    # break

            content = BeautifulSoup(content, 'lxml').text.strip()
            conn.execute(rawcontents.insert().values(rid=rid, content=content))
            # counter += Counter(jieba.lcut(content))
            # for w, f in counter.items():
                # if w not in stoplist:
                    # counter[w] += f
        except:
            logger.critical(rid)
            raise

# df = pd.DataFrame(list(counter.items()), columns=['word', 'freq'])
# df.sort_values('freq', ascending=False ,inplace=True)

# df.to_csv('WordFreq.csv', index=False)