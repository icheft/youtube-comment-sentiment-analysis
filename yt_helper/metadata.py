from __future__ import print_function
from dateutil.relativedelta import relativedelta
from collections import namedtuple
from datetime import datetime
import io
import json
import os
import sys
import time

import re
import requests
import pandas as pd

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v={youtube_id}'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

YT_CFG_RE = r'ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;'
YT_INITIAL_DATA_RE = r'(?:window\s*\[\s*["\']ytInitialData["\']\s*\]|ytInitialData)\s*=\s*({.+?})\s*;\s*(?:var\s+meta|</script|\n)'


def regex_search(text, pattern, group=1, default=None):
    match = re.search(pattern, text)
    return match.group(group) if match else default


def ajax_request(session, endpoint, ytcfg, retries=5, sleep=20):
    url = 'https://www.youtube.com' + \
        endpoint['commandMetadata']['webCommandMetadata']['apiUrl']

    data = {'context': ytcfg['INNERTUBE_CONTEXT'],
            'continuation': endpoint['continuationCommand']['token']}

    for _ in range(retries):
        response = session.post(
            url, params={'key': ytcfg['INNERTUBE_API_KEY']}, json=data)
        if response.status_code == 200:
            return response.json()
        if response.status_code in [403, 413]:
            return {}
        else:
            time.sleep(sleep)


def download_metadata(youtube_id, language=None):
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT

    response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))

    if 'uxe=' in response.request.url:
        session.cookies.set('CONSENT', 'YES+cb', domain='.youtube.com')
        response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))

    html = response.text
    # print(html)
    ytcfg = json.loads(regex_search(html, YT_CFG_RE, default=''))
    if not ytcfg:
        return  # Unable to extract configuration
    if language:
        ytcfg['INNERTUBE_CONTEXT']['client']['hl'] = language

    data = json.loads(regex_search(html, YT_INITIAL_DATA_RE, default=''))
    section = next(search_dict(data, 'playerOverlayVideoDetailsRenderer'))
    title = section['title']['simpleText']
    channel_name = section['subtitle']['runs'][0]['text']
    view_count = int(re.findall(
        r'\d+(?:,\d+)?', section['subtitle']['runs'][-1]['text'])[0].replace(',', ''))

    meta_data = namedtuple('metadata', ['title', 'channel_name', 'view_count'])
    meta_data = meta_data(
        title, channel_name, view_count
    )
    return meta_data


def search_dict(partial, search_key):
    stack = [partial]
    while stack:
        current_item = stack.pop()
        if isinstance(current_item, dict):
            for key, value in current_item.items():
                if key == search_key:
                    yield value
                else:
                    stack.append(value)
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)


def fetch(youtubeID: str = ''):

    print(f'Downloading metadata for video: {youtubeID}')

    return download_metadata(youtubeID, language='en')


if __name__ == "__main__":
    # SORT_BY_POPULAR = 0
    # SORT_BY_RECENT = 1
    youtubeID = 'a2nh9tm5oU8'
    print(fetch(youtubeID=youtubeID))
