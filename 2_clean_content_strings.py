from collections import Counter
from bs4 import BeautifulSoup
from sqlalchemy import select

from model.db import DB_ENGINE, rawcontents, replys
from utils.log import getLogger
import pandas as pd

logger = getLogger('clean')
counter = Counter()


rows = []
with DB_ENGINE.connect() as conn:
    s = select([replys.c.rid, replys.c.content]).where("replys.rid > 752958")

    for row in conn.execute(s):
        rid = row[replys.c.rid]
        content = row[replys.c.content]
        try:
            if rid % 0x100 == 0:
                logger.info(rid)

            content = BeautifulSoup(content, 'lxml').text.strip()
            conn.execute(rawcontents.insert().values(rid=rid, content=content))
        except:
            logger.critical(rid)
            raise
