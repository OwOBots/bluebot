import logging
import os
import sys

import praw
from atproto_client import Client
from dotenv import load_dotenv

load_dotenv()

LOG = logging.getLogger('login')
LOG.setLevel(logging.INFO)
file_handler = logging.FileHandler('login.log')
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
LOG.addHandler(file_handler)
LOG.addHandler(console_handler)


def ReqVars():
    required_vars = ['APU', 'AP', 'CID', 'CS']
    for var in required_vars:
        if var not in os.environ:
            LOG.critical(f"Error: {var} environment variable is not set")
            sys.exit(1)


# stolen from https://github.com/MarshalX/atproto/discussions/167#discussioncomment-8579573
class RateLimitedClient(Client):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self._limit = self._remaining = self._reset = None
    
    def get_rate_limit(self):
        return self._limit, self._remaining, self._reset
    
    def _invoke(self, *args, **kwargs):
        response = super()._invoke(*args, **kwargs)
        
        self._limit = response.headers.get('ratelimit-limit')
        self._remaining = response.headers.get('ratelimit-remaining')
        self._reset = response.headers.get('ratelimit-reset')
        
        return response


def blue_login():
    client = RateLimitedClient()
    client.login(os.environ["APU"], os.environ["AP"])


def reddit():
    reddit_praw = praw.Reddit(
        client_id=os.environ["CID"], client_secret=os.environ["CS"],
        user_agent="linux:bluebot:v0.1.6 (by /u/OwO_bots)"
        )
    return reddit_praw
