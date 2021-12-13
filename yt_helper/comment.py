from __future__ import print_function
from dateutil.relativedelta import relativedelta
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


def download_comments(youtube_id, sort_by=SORT_BY_RECENT, language=None, sleep=.1):
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT

    response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))

    if 'uxe=' in response.request.url:
        session.cookies.set('CONSENT', 'YES+cb', domain='.youtube.com')
        response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))

    html = response.text
    ytcfg = json.loads(regex_search(html, YT_CFG_RE, default=''))
    if not ytcfg:
        return  # Unable to extract configuration
    if language:
        ytcfg['INNERTUBE_CONTEXT']['client']['hl'] = language

    data = json.loads(regex_search(html, YT_INITIAL_DATA_RE, default=''))

    section = next(search_dict(data, 'itemSectionRenderer'), None)
    renderer = next(search_dict(
        section, 'continuationItemRenderer'), None) if section else None
    if not renderer:
        # Comments disabled?
        return

    needs_sorting = sort_by != SORT_BY_POPULAR
    continuations = [renderer['continuationEndpoint']]
    while continuations:
        continuation = continuations.pop()
        response = ajax_request(session, continuation, ytcfg)

        if not response:
            break
        if list(search_dict(response, 'externalErrorMessage')):
            raise RuntimeError('Error returned from server: ' +
                               next(search_dict(response, 'externalErrorMessage')))

        if needs_sorting:
            sort_menu = next(search_dict(response, 'sortFilterSubMenuRenderer'), {}).get(
                'subMenuItems', [])
            if sort_by < len(sort_menu):
                continuations = [sort_menu[sort_by]['serviceEndpoint']]
                needs_sorting = False
                continue
            raise RuntimeError('Failed to set sorting')

        actions = list(search_dict(response, 'reloadContinuationItemsCommand')) + \
            list(search_dict(response, 'appendContinuationItemsAction'))
        for action in actions:
            for item in action.get('continuationItems', []):
                if action['targetId'] == 'comments-section':
                    # Process continuations for comments and replies.
                    continuations[:0] = [ep for ep in search_dict(
                        item, 'continuationEndpoint')]
                if action['targetId'].startswith('comment-replies-item') and 'continuationItemRenderer' in item:
                    # Process the 'Show more replies' button
                    continuations.append(
                        next(search_dict(item, 'buttonRenderer'))['command'])

        for comment in reversed(list(search_dict(response, 'commentRenderer'))):
            # extract_vote(comment)
            vote, c_type = extract_vote(comment)
            yield {'cid': comment['commentId'],
                   'text': ''.join([c['text'] for c in comment['contentText'].get('runs', [])]),
                   'time': comment['publishedTimeText']['runs'][0]['text'],
                   'datetime': compute_time(comment['publishedTimeText']['runs'][0]['text']).strftime("%Y-%m-%d %H:%M:%S"),
                   'author': comment.get('authorText', {}).get('simpleText', ''),
                   'channel': comment['authorEndpoint']['browseEndpoint'].get('browseId', ''),
                   # comment.get('voteCount', {}).get('simpleText', '0'),
                   'type': c_type,
                   'votes': vote,
                   'heart': next(search_dict(comment, 'isHearted'), False)}

        time.sleep(sleep)


def extract_vote(comment) -> tuple([int, str]):
    # extracting vote the hard way
    target_entry = comment['actionButtons']['commentActionButtonsRenderer'][
        'likeButton']['toggleButtonRenderer']['accessibilityData']['accessibilityData']['label']
    m = re.search('Like this comment along with', target_entry)
    comment_type = 'comment'
    if not m:
        m = re.search('Like this reply along with', target_entry)
        comment_type = 'reply'
    vote_cnt = int(target_entry[m.end():].strip().split()[
        0].replace(',', ''))
    return vote_cnt, comment_type


def compute_time(time_txt):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc

    years, months, weeks, days, hours, minutes, seconds, microseconds
    """
    if "second" in time_txt:
        delta = int(time_txt.split()[0])
        time = datetime.now() - relativedelta(seconds=delta)
    elif "minute" in time_txt:
        delta = int(time_txt.split()[0])
        time = datetime.now() - relativedelta(minutes=delta)

    elif "hour" in time_txt:
        delta = int(time_txt.split()[0])
        time = datetime.now() - relativedelta(hours=delta)

    elif "yesterday" in time_txt.lower():
        time = datetime.now() - relativedelta(days=1)

    elif "day" in time_txt:
        delta = int(time_txt.split()[0])
        time = datetime.now() - relativedelta(days=delta)

    elif "week" in time_txt:
        delta = int(time_txt.split()[0])
        time = datetime.now() - relativedelta(weeks=delta)

    elif "month" in time_txt:
        delta = int(time_txt.split()[0])
        time = datetime.now() - relativedelta(months=delta)

    elif "year" in time_txt:
        delta = int(time_txt.split()[0])
        time = datetime.now() - relativedelta(years=delta)
    else:
        time = datetime.now()

    return time


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


def fetch(youtubeID: str = '', limit: int = None, language: str = 'en', sort: int = SORT_BY_RECENT, output: str = None):

    if output is not None:
        if os.sep in output:
            outdir = os.path.dirname()
            if not os.path.exists(outdir):
                os.makedirs(outdir)

    print(f'Downloading Youtube comments for video: {youtubeID}')
    count = 0
    all_comments = []
    start_time = time.time()

    if output is not None:
        with io.open(output, 'w', encoding='utf8') as fp:
            sys.stdout.write('Downloaded %d comment(s)\r' % count)
            sys.stdout.flush()
            start_time = time.time()
            for comment in download_comments(youtubeID, sort, language):
                comment_json = json.dumps(comment, ensure_ascii=False)
                print(comment_json.decode(
                    'utf-8') if isinstance(comment_json, bytes) else comment_json, file=fp)
                count += 1
                sys.stdout.write('Downloaded %d comment(s)\r' % count)
                sys.stdout.flush()
                if limit and count >= limit:
                    break
    for comment in download_comments(youtubeID, sort, language):
        comment_json = json.dumps(comment, ensure_ascii=False)
        sys.stdout.write('Downloaded %d comment(s)\r' % count)
        sys.stdout.flush()
        all_comments.append(pd.json_normalize(comment))
        count += 1
        sys.stdout.write('Downloaded %d comment(s)\r' % count)
        sys.stdout.flush()
        if limit and count >= limit:
            break
    df = pd.concat(all_comments, verify_integrity=True, ignore_index=True)
    print(f"\n[{(time.time() - start_time):.2f} seconds] Done!")
    return df


if __name__ == "__main__":
    # SORT_BY_POPULAR = 0
    # SORT_BY_RECENT = 1
    youtubeID = 'OscqgBj1HCw'
    df = fetch(youtubeID=youtubeID, limit=100,
               language='en', sort=SORT_BY_POPULAR, output=None)
    print(df.head())
