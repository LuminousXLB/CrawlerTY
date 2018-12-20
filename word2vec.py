import jieba
import pandas as pd

from app_db import DB_ENGINE
from settings import DATA_ROOT

titles = pd.read_sql('SELECT title FROM posts', con=DB_ENGINE)
replys = pd.read_sql('SELECT content FROM replys', con=DB_ENGINE)

def seperate(text):
    return jieba.lcut(text)

words = set()
