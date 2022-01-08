# IM 5054 Final Project 

## Environment Setup

Set up your virtual environment with `pipenv` (faster and lighter):

```shell
pip install pipenv
pipenv shell
pip install -r requirements.txt
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

