

from __future__ import (absolute_import, division, print_function, unicode_literals)

# import pip
# pip.main(['install', "scikit-surprise"])

# import surprise
from surprise import evaluate, print_perf, dump, Reader, Dataset
#import algorithms from surprise

from surprise import KNNBasic
from surprise import AlgoBase
from surprise import NMF
from surprise import SVD
from surprise import SlopeOne


from surprise import accuracy
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
np.random.seed(101)
from collections import defaultdict
import os, io, sys
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import config


mae1 = 0
rmse1 = 0

def blockPrint():
    sys.stdout = open(os.devnull, 'w')


def compute_recommendations():
    #connecting to the database
    # engine = create_engine("mysql://root:sesame@localhost/ratingsx?charset=utf8", echo=True)
    engine = create_engine(config.DB_URI, echo=True)
    session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))
# disable print



    blockPrint()

    #reading in the database
    df_ratings = pd.read_sql('SELECT * FROM ratings;', con = engine)
    df_ratings=df_ratings[['user_id','item_id','rating']]
    df_ratings = df_ratings.dropna()
    df_ratings = df_ratings.drop_duplicates()


    #formatting the dataset using the surprise library
    reader = Reader(line_format='user item rating', sep=',', rating_scale=(1, 5))
    data = Dataset.load_from_df(df_ratings, reader=reader)
    training_set = data.build_full_trainset()

    algorithm = KNNBasic()# use the singular value decomposition

    algorithm.train(training_set)# fit the data to the model
    testing_set = training_set.build_anti_testset()
    predictions = algorithm.test(testing_set)# make prediction


    #writing the function for top predictions
    def get_top_n(predictions, n=10):
#     Return the top-N recommendation for each user from a set of predictions.

#     Args:
#         predictions(list of Prediction objects): The list of predictions, as
#             returned by the test method of an algorithm.
#         n(int): The number of recommendation to output for each user. Default
#             is 10.

#     Returns:
#     A dict where keys are user (raw) ids and values are lists of tuples:
#         [(raw item id, rating estimation), ...] of size n.

    # First map the predictions to each user.
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n
# getting the top 10 predictions
    top_n = get_top_n(predictions, n=10)

# Print the recommended items for each user
    a = []
    for uid, user_ratings in top_n.items():
        a.append([uid, [iid for (iid, _) in user_ratings]])
    df_list_pred = pd.DataFrame.from_records(a,columns=['A','B'])


    df_user = pd.DataFrame(df_list_pred.A.values.tolist())
    df_pred = pd.DataFrame(df_list_pred.B.values.tolist())

    df_pred.columns = ['pred_1', 'pred_2','pred_3','pred_4',
                                   'pred_5','pred_6','pred_7','pred_8',
                                  'pred_9','pred_10']

    df_items = pd.read_sql('SELECT * FROM items;', con = engine)

    # df_pred = df_pred.applymap(lambda x: df_items.loc[x, 'title'])
    df_pred[['id']]=df_user
    df_pred = df_pred[['id','pred_1', 'pred_2','pred_3','pred_4',
                                   'pred_5','pred_6','pred_7','pred_8',
                                  'pred_9','pred_10']]

    df_pred['id'] = df_pred['id'].astype(int)

    # Append recomemndations
    df_pred.to_sql('recommendations',engine,if_exists='append', index=False)#if_exists='append'
    session.commit()

    #logging the predictions
    df_log = df_pred
    df_log['algorithm'] = 'KNNBasic'
    df_log = df_log.rename(columns={'id': 'user_id'})
    df_log = df_log[['user_id','pred_1', 'pred_2','pred_3','pred_4',
                                   'pred_5','pred_6','pred_7','pred_8',
                                  'pred_9','pred_10', 'algorithm']]

    df_log.to_sql('predictionlogs',engine,if_exists='append', index=False)#if_exists='append'
    session.commit()

    global mae1
    global rmse1
    mae1 = accuracy.mae(predictions)
    rmse1 = accuracy.rmse(predictions)
    mae1 = float(mae1)
    rmse1 = float(rmse1)
