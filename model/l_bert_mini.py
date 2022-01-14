import joblib
import yt_helper
from keras_bert import extract_embeddings
import streamlit as st
import pandas as pd
import numpy as np
import sys

sys.path.append("..")


@st.cache
def load_model():
    return joblib.load('model/BERTModel-mini')


pretrained_path = 'model/BERT-mini'


def yt_comment_preprocess(processed_dataset):

    test_data = processed_dataset['comment']

    embeddings_test = extract_embeddings(pretrained_path, test_data)
    x_test = []
    for i in range(len(test_data)):
        x_test.append(embeddings_test[i][0])

    return x_test


def predict_result(youtubeID):
    SORT_BY_POPULAR = 1
    SORT_BY_RECENT = 0

    limit = 200  # set to None to download all comments
    sort = SORT_BY_POPULAR
    output = None  # do not write out files

    df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                 language='en', sort=sort, output=output)

    x_test = yt_comment_preprocess(df, limit)
    task_model = load_model()
    y_pred = task_model.predict(x_test)
    positive_rate = (y_pred >= 0.5).sum() / y_pred.shape[0]
    nagative_rate = (y_pred < 0.5).sum() / y_pred.shape[0]
    return positive_rate, nagative_rate


def l_bert_V3(processed_dataset: pd.DataFrame):
    # print('len: ', len(processed_dataset))
    x_test = yt_comment_preprocess(processed_dataset)
    task_model = load_model()
    y_pred = task_model.predict(x_test)
    positive_rate = (y_pred >= 0.5).sum() / y_pred.shape[0]
    nagative_rate = (y_pred < 0.5).sum() / y_pred.shape[0]
    return positive_rate, nagative_rate
