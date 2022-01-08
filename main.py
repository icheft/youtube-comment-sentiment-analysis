import yt_helper
SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

if __name__ == '__main__':

    raw_url = "http://www.youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index"
    youtubeID = yt_helper.parser.url(raw_url)  # 0zM3nApSvMg

    limit = 100
    sort = SORT_BY_POPULAR
    output = None  # do not write out files

    metadata = yt_helper.metadata.fetch(youtubeID=youtubeID)

    # print(metadata.title, metadata.channel_name, metadata.view_count)
    print(metadata)

    df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                 language='en', sort=sort, output=output)
    print(df.head())
