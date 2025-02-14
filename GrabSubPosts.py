import configparser as config
import sys

import praw

import SetupLogging
import globals

parser = config.ConfigParser()
parser.read('config.ini')

LOG = SetupLogging.setup_logger('grabsubposts', 'grabsubposts.log')


def Login(CID, CS):
    """
    Logs into Reddit using the provided client ID and client secret.
    :param CID:
    :param CS:
    :return:
    """
    reddit = praw.Reddit(
        client_id=CID, client_secret=CS,
        user_agent=f"linux:bluebot:v{globals.VERSION} (by /u/OwO_bots)"
        )
    return reddit


# there's a way better way to do this, but I'm too lazy to figure it out
# if you know a better way, please let me know
def get_subreddit(CID, CS):
    """
    Retrieves the subreddit specified in the configuration file.

    Returns:
        praw.models.Subreddit: The subreddit object for the specified subreddit.

    Raises:
        SystemExit: If the 'reddit' section or 'subreddit' key is not found in the config file.
    """
    reddit = Login(CID, CS)
    try:
        sub = parser.get('reddit', 'subreddit')
        LOG.info(f"Trying to access subreddit: {sub}")
        return reddit.subreddit(sub)
    except config.NoSectionError:
        LOG.error("Error: 'reddit' section not found in config file")
        sys.exit(1)
    except config.NoOptionError:
        LOG.error("Error: 'subreddit' key not found in 'reddit' section of config file")
        sys.exit(1)
