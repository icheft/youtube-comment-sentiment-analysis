import yt_helper
import pandas as pd

from yt_helper import comment
SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

if __name__ == '__main__':

    videoID = ['rfscVS0vtbw&t=35s&ab_channel=freeCodeCamp.org', 'V7WtQYLmwlI&list=RDV7WtQYLmwlI&start_radio=1&ab_channel=EleniDrake', 'BVhGuuTalcU&ab_channel=OscarStinson']
    dfList = []
    for i in range(len(videoID)):
        youtubeID = videoID[i]
        limit = 100
        sort = SORT_BY_POPULAR
        output = None  # do not write out files

        df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                        language='en', sort=sort, output=output)

        processed_dataset = yt_helper.comment.preprocessing(df=df, emoji_to_word=True)
        comment_only = processed_dataset[['comment']].copy()
        dfList.append(comment_only)
    result = pd.concat(dfList, ignore_index=True)
    result.to_excel('output.xlsx', index=True)
    