# IM 5054 Final Project 

## Environment Setup

Set up your virtual environment with `pipenv` (faster and lighter):

```shell
pip install pipenv
pipenv shell
pip install -r requirements.txt
```

Then every time you enter this repository, be sure to activate the virtual environment.

## Data Fetching

```py
import yt_downloader

SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1


youtubeID = 'OscqgBj1HCw'
limit = 100
sort = SORT_BY_POPULAR
output = None  # do not write out files

df = yt_downloader.comment.download_helper(youtubeID=youtubeID, limit=limit,
                                            language='en', sort=sort, output=output)
print(df.head())
```

