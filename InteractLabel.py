from app_db import DB_ENGINE, rawcontents
from sqlalchemy import update

stmt = 'SELECT * FROM rawcontents WHERE content LIKE "%点赞 |  打赏 | 回复%" AND assure=0'

with DB_ENGINE.connect() as conn:
    for row in conn.execute(stmt):
        print('\n')
        print(row['content'])

        choice = input('\n\t这是水帖吗？[Y/n] ')
        transcation = conn.begin()
        try:
            if choice in ['n', 'N']:
            # if choice in ['Y', 'y']:
                choice = 0
            else:
                choice = 1

            conn.execute(
                update(rawcontents)
                .where(rawcontents.c.rid == row['rid'])
                .values(tag=choice, assure=True)
            )

            transcation.commit()
        except:
            transcation.rollback()
            print('\n==========  failed  ==========\n')
            raise
        else:
            print('\n==========  success  ==========\n')
