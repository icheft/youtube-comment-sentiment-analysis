#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from tensorflow import keras
from keras.datasets import imdb
from keras import preprocessing

import sys
sys.path.append("..")
import yt_helper

max_unique_tokens = 20000 # 取前20000個字來建立特徵維度
max_DocLen = 200 # 限定文件長度度為前200字
model = keras.models.load_model('model_Dragons/taskBasedModel')


def yt_comment_preprocess(df):
    processed_dataset = yt_helper.comment.preprocessing(df=df, emoji_to_word=True) 
    yt_data = processed_dataset["comment"].tolist()
    yt_data = [x.split() for x in yt_data]
    word_index = imdb.get_word_index()
    test_data2 = []
    for comment in yt_data:
        temp = []
        for word in comment:
            try:
                if word_index[word.lower()] < max_unique_tokens:
                    temp.append(word_index[word.lower()])
            except:
                pass
        test_data2.append(temp) 
    test_data2 = preprocessing.sequence.pad_sequences(test_data2, maxlen=max_DocLen, truncating='post', padding='post')
    return test_data2

## 預測新進資料(backend service)
def dl_taskbased(youtubeID):
    SORT_BY_POPULAR = 1
    SORT_BY_RECENT = 0


    limit = 100 # set to None to download all comments
    sort = SORT_BY_POPULAR
    output = None  # do not write out files

    df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                                language='en', sort=sort, output=output)
#     display(df.head())
    test_data2 = yt_comment_preprocess(df)
#     print(test_data2.shape)
    result = model.predict(test_data2)
    positive_rate = (result >= 0.5).sum() / result.shape[0]
    nagative_rate = (result < 0.5).sum() / result.shape[0]
    return positive_rate, nagative_rate


# youtubeID = 'OscqgBj1HCw'
# dl_taskbased(youtubeID)

