import plotly.express as px
import plotly.graph_objects as go
import io
import pandas as pd
import yt_helper
import os
from streamlit_lottie import st_lottie
import requests
import streamlit as st

LOGO_URL = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/fire_1f525.png"
SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1


# Set page title and favicon.
st.set_page_config(
    page_title="YouTube Comment Analysis",
    page_icon=LOGO_URL, layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': '''An app prototype made by us for the purpose of analyzing the comments of YouTube videos.'''
    }
)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def pie_chart(df, values='tip', names='day', color='day'):
    color_discrete_map = {'Like': '#FA0606',
                          'Dislike': '#FC8C94',
                          'Neutral': '#848484', }

    fig = px.pie(df, values=values, names=names, color=color, labels={names: 'Label', values: 'Count'},
                 color_discrete_map=color_discrete_map)
    fig.update_traces(hoverinfo='label+percent', textinfo='percent+label', textfont_size=20,
                      marker_line=dict(color='#000000', width=2))
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=400)
    return fig


@ st.cache
def get_data(youtubeID="", limit=100, options={}):
    sort = SORT_BY_POPULAR
    output = None  # do not write out files

    df = yt_helper.comment.fetch(youtubeID=youtubeID, limit=limit,
                                 language='en', sort=sort, output=output)

    processed_dataset = yt_helper.comment.preprocessing(
        df=df, emoji_to_word=options['emoji'])

    if not options['neutral']:
        processed_dataset = processed_dataset[processed_dataset['pol_category'] != 0]
    if options['vote']:
        processed_dataset = processed_dataset[processed_dataset['votes'] > 0]

    return processed_dataset


def app():
    # sidebar gadgets
    row0_spacer1, row0_1, row0_spacer2 = st.columns((.1, 3.2, .1))
    row0_1.title('YouTube Comment Sentiment Analysis')

    row1_spacer1, row1_1, row1_spacer2 = st.columns((.1, 3.2, .1))

    with row1_1:
        st.markdown(
            "Not sure the quality of a YouTube video? Let's find out using the comment section of the video.")
        st.markdown(
            "**To begin, please enter the link to the YouTube video you wish to analyze** 👇")

    options = dict()
    row2_spacer1, row2_1, row2_spacer2 = st.columns((.1, 3.2, .1))
    with row2_1:
        raw_url = st.text_input(
            "Input a YouTube video link (e.g. https://www.youtube.com/watch?v=0zM3nApSvMg) or a YouTube video ID (e.g. 0zM3nApSvMg)")
        need_help = st.expander('Need help? 👉')
        with need_help:
            st.markdown(
                "Not sure what to put in? It will work as long as it is a valid YouTube link :wink:")
    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.columns(
        (.1, 1.6, .1, 1.6, .1))
    with row3_1:
        options['limit'] = st.number_input(
            'Comment limit you wish to set (the lower the limit is, the faster the analysis will be)', value=100, min_value=1)
    with row3_2:
        options['neutral'] = st.checkbox('Include neutral comments')
        options['vote'] = st.checkbox('Include only comments with votes')
        options['emoji'] = st.checkbox('Consider emoji as a feature')

    if raw_url:
        row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
        youtubeID = yt_helper.parser.url(raw_url)  # 0zM3nApSvMg
        df = get_data(youtubeID=youtubeID,
                      limit=options['limit'], options=options)
        tmp_df = df.copy()

        with row3_1:
            st.write(tmp_df.head())

        row4_spacer1, row4_1, _, row4_2, row4_spacer1 = st.columns(
            (.09, 1.2, .1, 1.2, .1))

        with row4_1:
            st.download_button(
                label=f"📓 Download (raw_data.csv)",
                data=yt_helper.utils.convert_df(tmp_df),
                file_name=f'raw_data.csv',
                mime='text/csv',
            )

        row5_spacer1, row5_1, row5_spacer2 = st.columns((.1, 3.2, .1))
        tmp_df['label'] = tmp_df['pol_category'].apply(
            lambda x: 'Like' if x == 1 else 'Dislike' if x == -1 else 'Neutral')
        label_cnt = tmp_df.groupby(
            'label').count().reset_index('label')
        # st.write(label_cnt)
        fig = pie_chart(label_cnt, values='pol_category',
                        names='label', color='label')
        st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    lottie_yt = load_lottieurl(
        'https://assets7.lottiefiles.com/packages/lf20_EAfMOs/Youtube.json')
    st_lottie(lottie_yt, speed=1, height=200, key="initial")

    app()
