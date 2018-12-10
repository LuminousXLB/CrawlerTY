import jieba
import pandas as pd

from app_db import DB_ENGINE
from settings import DATA_ROOT

def dump_isForward(path):
    titles = pd.read_sql('SELECT pid, title FROM posts', con=DB_ENGINE, index_col='pid')

    INDICATORS = '转 转载 转帖 转自'.split(' ')
    def isForward(text):
        for word in jieba.cut(text):
            if word in INDICATORS:
                return True
        return False

    df = titles.merge(titles.applymap(isForward), on='pid')

    df = df.rename({
        'title_x': 'title',
        'title_y': 'isForward'
    }, axis='columns')

    zhuan = titles.merge(titles.applymap(lambda x: x.find('转') > -1), on='pid')
    zhuan = zhuan[zhuan['title_y']].merge(pd.DataFrame(df['isForward']), on='pid', how='left')

    zhuan.to_excel(path)



if __name__ == "__main__":
    dump_isForward(DATA_ROOT/'isForward.xlsx')