import yt_helper
SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

if __name__ == '__main__':
    youtubeID = 'OscqgBj1HCw'
    youtubeID = 'V7WtQYLmwlI&ab_channel=EleniDrake'
    limit = 300
    sort = SORT_BY_POPULAR
    output = None  # do not write out files

    df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                 language='en', sort=sort, output=output)

    processed_dataset = yt_helper.comment.preprocessing(df=df, emoji_to_word=False)
    print(processed_dataset.head())
    print(processed_dataset['pol_category'].value_counts())
    
    

    