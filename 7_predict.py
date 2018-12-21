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


logger.info('Load the model')

with open('SVC_rbf_model.bin', 'rb') as f:
    clf = pickle.load(f)


logger.info('Start predicting')


def predict(begin, end, step):
    for lh in range(begin, end, step):
        logger.info('Start predict {}'.format(lh))

        df = pd.read_sql(
            'SELECT rid, vector FROM rawcontents WHERE rid >= {} LIMIT {}'.format(
                lh, step
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


if __name__ == "__main__":
    predict(0, 1587781, 0x400)
