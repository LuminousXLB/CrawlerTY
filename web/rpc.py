import logging
import os
import pickle
from pprint import pprint

import numpy as np
import pandas as pd
import zerorpc
from sklearn.linear_model import SGDClassifier
from sqlalchemy import update

from model.db import DB_ENGINE, rawcontents
from utils.log import getLogger

logger = getLogger('semiTrain')


def fetchAllData(threshold):
    return pd.read_sql(
        'SELECT rid, tag, assure FROM rawcontents WHERE LENGTH(content) > {}'.format(
            threshold),
        DB_ENGINE
    )


def randomSelectData(data, count):
    inds = np.arange(len(data))
    np.random.shuffle(inds)
    return data.iloc[inds[:count]].copy()


def completeTrainData(current):
    stmt = 'SELECT rid, content, vector FROM rawcontents WHERE rid IN {}'

    with DB_ENGINE.connect() as conn:
        traindata = current.merge(
            pd.DataFrame(
                conn.execute(
                    stmt.format(tuple(current['rid'].values))
                ).fetchall(),
                columns=['rid', 'content', 'vector']
            ),
            on='rid'
        )

    traindata['ss'] = list(map(
        lambda x: -1 if x[0] < 0.5 else x[1],
        zip(traindata['assure'], traindata['tag'])
    ))
    traindata['vector'] = traindata['vector'].apply(pickle.loads)

    return traindata.set_index(np.arange(len(current)))


def extractData(df):
    return list(df['vector'].values), list(df['tag'].values)


def refresh(threshold, trainscale):
    #####################################################

    logger.info('==== New Round Start ====')

    #####################################################

    logger.info('Read Database ...')
    all_data = fetchAllData(100)
    logger.info('Complete.')

    #####################################################

    logger.info('Prepare train data ...')
    labeled = all_data[all_data['assure'] > 0.5].copy()
    labeled = completeTrainData(labeled)

    print(labeled.describe())

    logger.info('Complete')

    #####################################################

    logger.info('Prepare predicted data ...')
    predicted = all_data[all_data['assure'] < 0.5].copy()
    predicted = completeTrainData(randomSelectData(predicted, trainscale))
    logger.info('Complete')

    #####################################################

    logger.info('Fit ...')

    del all_data

    clf = SGDClassifier(
        random_state=ord(os.urandom(1)),
        max_iter=512,
        tol=1e-3,
        penalty='elasticnet',
        loss='modified_huber',
        fit_intercept=False
    )

    X_labeled, y_labeled = extractData(labeled)
    clf_fit_result = clf.fit(X_labeled, y_labeled)

    logger.info('Complete')

    #####################################################

    logger.info('Predict ...')

    X_predicted, _ = extractData(predicted)
    y_predicted = clf_fit_result.predict(X_predicted)

    predicted['predict'] = y_predicted

    print(predicted.describe())

    return predicted


predicted = refresh(300, 2)
i = 0
counter = [[0, 0], [0, 0]]


def argedrefresh():
    global predicted
    predicted = refresh(100, 256)


class semi_supervise_train(object):
    T = ['T', 'Y', '1', 'y', 't', 'z', 1, 1.]
    F = ['F', 'N', '0', 'n', 'f', 'x', 0, 0.]

    def __init__(self):
        global predicted, i
        if i >= len(predicted):
            argedrefresh()

    def labelRequest(self):
        global predicted, i

        if i >= len(predicted):
            argedrefresh()

        row = predicted.iloc[i]

        i += 1

        return i, len(predicted), row.content, int(row.rid), row.predict
        # {
        #     'index': i,
        #     'total': len(predicted),
        #     'content': row.content,
        #     'rid': int(row.rid),
        #     'predict': row.predict
        # }
        # print(row.content)
        # print('\n')
        # print(
        #     '[{} / {}]'.format(i, len(self.predicted)),
        #     'rid', row.rid,
        #     'predict', row.predict
        # )

        # choice = input(
        #     '-- \t这是水帖吗？[{}] '.format('是' if row.predict > 0.5 else '否')
        # )

    def label(self, rid, choice):
        try:
            global counter

            tag = None
            if choice in self.T:
                tag = 1
            elif choice in self.F:
                tag = 0

            assert(tag in [0, 1])

            with DB_ENGINE.connect() as conn:
                conn.execute(
                    'UPDATE rawcontents SET tag={}, assure=True WHERE rid={}'.format(
                        tag, rid
                    )
                )

        except:
            logger.info('Failed to label {} to {}'.format(rid, tag))
            return i, len(predicted), 'fail'
        else:
            logger.info('Success in labeling {} to {}'.format(rid, tag))
            return i, len(predicted), 'success'


s = zerorpc.Server(semi_supervise_train())
s.bind("tcp://127.0.0.1:8989")
s.run()
