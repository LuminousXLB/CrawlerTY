from app_db import DB_ENGINE, rawcontents
from sqlalchemy import update

bushui = []
# bushui = [794858, 881226 ]

shuicontent = ['口令  赞一个呗\n   \n\n    抢红包',
 '点赞是一种美德',
 '麻烦点个赞吧\n   \n\n    抢红包',
 '互赞必回',
 '已赞主楼',
 '大家点赞必回',
 '互赞来下',
 '主楼已赞',
 '给你赞',
 '已点赞（｡ò ∀ ó｡）',
 '口令  互赞\n   \n\n    抢红包',
 '沙发赞。',
 '表示已赞',
 '点赞的一生平安',
 '感谢楼主 疯狂赞',
 '已赞楼主 强烈支持 收到请回\n \n\n 预定一个前排座位 坐等帖子大火',
 '来赞了。',
 '点赞领红包',
 '主贴赞了',
 '怎么抢红包？已赞！',
 '捡到个红包点个赞',
 '点赞者行好运。\n   \n\n    抢红包',
 '今天楼里点赞的多起来了。上小的。。。',
 '继续点赞',
 '领包点赞双赢\n   \n\n    抢红包',
 '赞搂至\n   \n\n    抢红包',
 '点赞的三宫六院七十二妃！\n   \n\n    抢红包',
 '点赞包\n   \n\n    抢红包']

with DB_ENGINE.connect() as conn:
    transcation = conn.begin()
    try:
        for content in shuicontent:
            print(content)
            conn.execute(
                update(rawcontents)
                .where(rawcontents.c.content == content)
                .values(tag=1.0, assure=True)
            )

        # for rid in shui:
        #     conn.execute(
        #         update(rawcontents)
        #         .where(rawcontents.c.rid == rid)
        #         .values(tag=1.0, assure=True)
        #     )

        for rid in bushui:
            conn.execute(
                update(rawcontents)
                .where(rawcontents.c.rid == rid)
                .values(tag=0.0, assure=True)
            )

        print('commit')
        transcation.commit()
    except:
        transcation.rollback()
        print('failed')
    else:
        print('success')
