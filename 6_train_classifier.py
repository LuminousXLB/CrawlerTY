from utils.log import getLogger
import pandas as pd
from model.db import DB_ENGINE
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_val_score
import numpy as np
import pickle
import os
from sklearn import ensemble, svm

logger = getLogger('predict')


labeled = pd.read_sql(
    'SELECT rid, tag, vector FROM rawcontents WHERE assure>0.5',
    DB_ENGINE
)

train = labeled.groupby('vector')['tag'].mean()

X = list(pd.Series(train.index).apply(pickle.loads))
y = list(train.values)

logger.info('Build the model')

clf = svm.SVC(kernel='rbf')

logger.info('Fitting...')

clf.fit(X, y)

with open(DATA_ROOT/'SVC_rbf_model.bin', 'wb') as f:
    pickle.dump(clf, f)
