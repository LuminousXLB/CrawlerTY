from utils_log import getLogger
import pandas as pd
from app_db import DB_ENGINE
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_val_score
import numpy as np
import pickle
import os
from sklearn import ensemble, svm

logger = getLogger('predict')

# labeled = pd.read_sql(
#     'SELECT rid, tag, vector FROM rawcontents WHERE assure>0.5',
#     DB_ENGINE
# )

# train = labeled.groupby('vector')['tag'].mean()

# X = list(pd.Series(train.index).apply(pickle.loads))
# y = list(train.values)

# logger.info('Load train dataset')

# with open('train_data_X.bin', 'rb') as f:
#     X = pickle.load(f)

# with open('train_data_y.bin', 'rb') as f:
#     y = pickle.load(f)

# logger.info('Build the model')

# clf = svm.SVC(kernel='rbf')

# logger.info('Fitting...')

# clf.fit(X, y)

# with open('SVC_rbf_model.bin', 'wb') as f:
#     pickle.dump(clf, f)


logger.info('Load the model')

with open('SVC_rbf_model.bin', 'rb') as f:
    clf = pickle.load(f)


logger.info('Start predicting')

# for lh in range(59904, 500000, 0x400):
for lh in range(500000, 1000000, 0x400):
# for lh in range(1000000, 1587968, 0x400):
    logger.info('Start predict {}'.format(lh))

    df = pd.read_sql(
        'SELECT rid, vector FROM rawcontents WHERE rid >= {} AND rid < {}'.format(
            lh, lh+0x400
        ), DB_ENGINE
    )
    X = df['vector'].apply(pickle.loads)
    df['predict'] = clf.predict(list(X))

    logger.info('dump {}'.format(lh))

    T = df[df['predict'] > 0.5].rid.values
    F = df[df['predict'] < 0.5].rid.values

    with DB_ENGINE.connect() as conn:
        transcation = conn.begin()
        try:
            conn.execute(
                'UPDATE rawcontents SET predict=1 WHERE rid IN {}'.format(tuple(T))
            )

            conn.execute(
                'UPDATE rawcontents SET predict=0 WHERE rid IN {}'.format(tuple(F))
            )

            transcation.commit()
        except:
            transcation.rollback()
            logger.warning('Interrupted at {}'.format(lh))
            raise

        else:
            logger.info('Success at {}'.format(lh))
