import os
from dotenv import load_dotenv
from youtube_easy_api.easy_wrapper import *

load_dotenv()

API_KEY = os.getenv('key')

easy_wrapper = YoutubeEasyWrapper()
easy_wrapper.initialize(api_key=API_KEY)
metadata = easy_wrapper.get_metadata(video_id="ScMzIvxBSi4")  # ScMzIvxBSi4

print(len(metadata['comments']))
