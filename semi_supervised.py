import logging
import os
import pickle
from pprint import pprint

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sqlalchemy import update

from app_db import DB_ENGINE, rawcontents
from utils_log import getLogger

logger = getLogger('semiTrain')


def fetchAllData(threshold):
    return pd.read_sql(
        'SELECT rid, tag, assure FROM rawcontents WHERE LENGTH(content) > {}'.format(threshold),
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


#####################################################

logger.info('==== New Round Start ====')

#####################################################

logger.info('Read Database ...')
all_data = fetchAllData(50)
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
predicted = completeTrainData(randomSelectData(predicted, 64))
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

input('continue...')

counter = [
    [0, 0],
    [0, 0]
]

for i in range(len(predicted)):
    print("#####################################################")
    row = predicted.iloc[i]

    print(row.content)
    print('\n')
    print(
        '[{} / {}]'.format(i, len(predicted)),
        'rid', row.rid,
        'predict', row.predict
    )

    choice = input(
        '-- \t这是水帖吗？[{}][z=0, x=1] '.format('是' if row.predict > 0.5 else '否')
    )

    try:
        if choice in ['n', 'N', '0', 'z', '[']:
            choice = 0
        elif choice in ['Y', 'y', '1', 'x', ']']:
            choice = 1
        elif choice == '':
            choice = 1 if row.predict > 0.5 else 0

        assert(choice in [0, 1])

        with DB_ENGINE.connect() as conn:
            conn.execute(
                'UPDATE rawcontents SET tag={}, assure=True WHERE rid={}'.format(
                    choice, row.rid
                )
            )

        counter[row.predict > 0.5][choice] += 1

    except:
        logger.info('Failed to label {} to {}'.format(row.rid, choice))
        raise
    else:
        logger.info('Success in labeling {} to {}'.format(row.rid, choice))
    finally:
        pprint(counter)
