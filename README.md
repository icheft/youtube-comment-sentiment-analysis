<h1 align="center">
  <br>
  <a href="https://share.streamlit.io/icheft/youtube-comment-sentiment-analysis/main/app.py"><img src="assets/img/youtube.png" alt="yt-logo" width="75"></a>
  <br>
  YouTube Comment Sentiment Analysis
  <br>
</h1>

<h4 align="center">IM 5054 Final Project by Group 14</h4>

<p align="center">
  <a href="https://share.streamlit.io/icheft/youtube-comment-sentiment-analysis/main/app.py">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg"
         alt="Open in Streamlit">
  </a>
</p>

<p align="center">
  <a href="#environment-setup">Environment Setup</a> •
  <a href="#yt-helper">YT Helper</a> •
  <a href="#models">Models</a> •
  <a href="#application">Application</a> •
  <a href="#contributions">Contributions</a>
</p>

## Environment Setup

Set up your virtual environment with `pipenv` (faster and lighter):

```shell
pip install pipenv
pipenv install
pipenv shell
```

Then every time you enter this repository, be sure to activate the virtual environment.

## YT Helper

`yt_helper` provides some data fetching and preprocessing functions to ease the further development of this project.

### Data Fetching

```py
import yt_helper

SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1


youtubeID = 'OscqgBj1HCw'
limit = 100 # set to None to download all comments
sort = SORT_BY_POPULAR
output = None  # do not write out files

df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                            language='en', sort=sort, output=output)
print(df.head())
```

#### Metadata

```py
import yt_helper

metadata = yt_helper.metadata.fetch(youtubeID=youtubeID)

# print(metadata.title, metadata.channel_name, metadata.view_count)
print(metadata)
```

### URL Parsing

You can use it together with `yt_helper.comment.fetch`:

```py
import yt_helper

raw_url = "http://www.youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index"
youtubeID = yt_helper.parser.url(raw_url) # 0zM3nApSvMg

limit = 100 # set to None to download all comments
sort = SORT_BY_POPULAR
output = None  # do not write out files

df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                            language='en', sort=sort, output=output)
```

### Data Preprocessing

`yt_helper.comment.preprocessing` can help transfer comments fetched with crawler to a clean format.  
The preprocessing methods used includes:  
1. drop duplicate comments with same comment ID
2. remove emojis / transfer emojis to words
3. reserve English comments only (can be omitted if the model can support multilingual prediction)
4. remove brackets and special characters
5. data labelling by existing model, TextBlob

Example usage:  
```py
processed_dataset = yt_helper.comment.preprocessing(df=df, emoji_to_word=True)
```
Parameters explanation:  
1. `df` : raw dataframe haven't been preprocessed yet. (Just fetched by crawler)
2. `emoji_to_word` : If you want to eliminate emoticons entirely, set to `False` . If you want to transfer emoticons to words, set to `True`. 


## Models
### taskBasedModel

#### V1

`model.dl_taskbased` is a function that takes youtubeID as input and returns sentiment ratios as output.

```py
from model.dl_taskbased import dl_taskbased

pos, neg = dl_taskbased(youtubeID = "OscqgBj1HCw") # output: (positive ratio, negative ratio) 
```

#### V2

`model.dl_taskbased_V2` takes in a DataFrame (usually preprocessed by `yt_helper.comment.preprocessing`) as input and returns sentiment ratios as output.

You can see the actual usage in `app.py`.

```py
import yt_helper
from model.dl_taskbased import dl_taskbased_V2

SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

sort = SORT_BY_POPULAR
output = None  # do not write out files

youtubeID = "OscqgBj1HCw"
limit = 100
emoji = True

df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                 language='en', sort=sort, output=output)
processed_dataset = yt_helper.comment.preprocessing(
    df=df, emoji_to_word=emoji)

pos, neg = dl_taskbased_V2(processed_dataset=processed_dataset)
```

### BERT-mini

`model.l_bert_mini` uses BERT word embedding to help the training process. To get the positive and negative ratios, you can use the following code:

```py
import yt_helper
from model.l_bert_mini import l_bert_V3

SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

sort = SORT_BY_POPULAR
output = None  # do not write out files

youtubeID = "OscqgBj1HCw"
limit = 100
emoji = True

df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                 language='en', sort=sort, output=output)
processed_dataset = yt_helper.comment.preprocessing(
    df=df, emoji_to_word=emoji)

pos, neg = l_bert_V3(processed_dataset)
```

## Application

To run the application locally, first make sure you have the environment set up right, and then simply start the `app.py` file by running:

```py
streamlit run app.py
```

You're good to go. 

## Contributions

We know that our models do not perform well on some videos due to our lack of labeled data. 

If you have any suggestions or are willing to help, please let us know. We are open to any issues and pull requests.