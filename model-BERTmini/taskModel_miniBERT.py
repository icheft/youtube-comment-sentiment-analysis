#!/usr/bin/env python
# coding: utf-8
from keras_bert import extract_embeddings

import pandas as pd
import numpy as np
import sys
sys.path.append("..")
import yt_helper

import joblib
task_model = joblib.load('BERTModel-mini')
pretrained_path = './BERT-mini'

def yt_comment_preprocess(df, limit):
    processed_dataset = yt_helper.comment.preprocessing(df=df, emoji_to_word=True) 
    test_data = processed_dataset['regular_text']
    
    embeddings_test = extract_embeddings(pretrained_path, test_data)
    x_test = []
    for i in range(limit):
        x_test.append(embeddings_test[i][0])
        
    return x_test

def predict_result(youtubeID):
    SORT_BY_POPULAR = 1
    SORT_BY_RECENT = 0

    limit = 200 # set to None to download all comments
    sort = SORT_BY_POPULAR
    output = None  # do not write out files

    df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                                language='en', sort=sort, output=output)

    x_test = yt_comment_preprocess(df, limit)
    y_pred = task_model.predict(x_test)
    positive_rate = (y_pred >= 0.5).sum() / y_pred.shape[0]
    nagative_rate = (y_pred < 0.5).sum() / y_pred.shape[0]
    return positive_rate, nagative_rate

# youtubeID = 'OscqgBj1HCw'
# predict_result(youtubeID)