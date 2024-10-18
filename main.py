#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser as config
import csv
import logging
import math
import os
import sys
import time

import atproto
import dotenv
import praw
import prawcore
import requests

# this is dumb
LOG = logging.getLogger('bluebot')
LOG.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('bluebot.log')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
LOG.addHandler(file_handler)
LOG.addHandler(console_handler)
LOG.debug("goofy ahh logger test")

parser = config.ConfigParser()
parser.read('config.ini')

dotenv.load_dotenv()

# Check if required environment variables are set
required_vars = ['APU', 'AP', 'CID', 'CS']
for var in required_vars:
    if var not in os.environ:
        LOG.critical(f"Error: {var} environment variable is not set")
        sys.exit(1)

client = atproto.Client()
client.login(os.environ["APU"], os.environ["AP"])

reddit = praw.Reddit(client_id=os.environ["CID"], client_secret=os.environ["CS"],
                     user_agent="linux:bluebot:v0.0.1 (by /u/dariusisdumblol)")


def duplicate_check(id):
    value = False
    with open('posted_images.csv', 'rt', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if id in row:
                value = True
    f.close()
    return value


# stolen from gitlab.com/mocchapi/tootbotX
def notify_sleep(sleeptime, interval=5 * 60, reason=""):
    """Sleeps for `sleeptime` amount of time, notifying the user every `interval` seconds.
    Optionally supplied with a `reason`, which gets appended to the first message"""
    timechunk = sleeptime / interval
    timeleft = sleeptime
    LOG.info(f"Sleeping for {round(sleeptime / 60, 1)}m" + reason)
    loop2 = False
    while math.floor(timeleft) > 0:
        zzzz = 0
        if sleeptime > interval:
            zzzz = interval
        else:
            zzzz = timeleft

        if loop2:
            LOG.info(f"{round(timeleft / 60, 1)}m remaining.")
        else:
            loop2 = True
        timeleft -= zzzz
        time.sleep(zzzz)


def get_subreddit():
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


def main():
    LOG.info("Starting...")
    client.login(os.environ["APU"], os.environ["AP"])
    try:
        limit = int(parser.get('reddit', 'limit'))
    except config.NoSectionError:
        LOG.error("Error: 'reddit' section not found in config file")
        sys.exit(1)
    except config.NoOptionError:
        LOG.error("Error: 'limit' key not found in 'reddit' section of config file")
        sys.exit(1)
    except ValueError:
        LOG.error("Error: 'limit' value is not a valid integer")
        sys.exit(1)
    last_post_id = None
    try:
        sub = get_subreddit()
        with open('posted_images.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            posted_images = set(row[0] for row in reader)

        new_posts_found = False
        for submission in sub.new(limit=limit):
            post_id = submission.id
            if not submission.stickied:
                LOG.info(f"{submission.title} ({submission.author.name})")
                image_url = submission.preview['images'][0]['source']['url']
                if not duplicate_check(post_id):
                    image_data = requests.get(image_url).content
                    # TODO: add ocr
                    client.send_image(
                        text=submission.title + " (u/" + submission.author.name + ")" + "  " + submission.url,
                                      image=image_data,
                                      image_alt='')
                    with open('posted_images.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([post_id])
                    LOG.info(f"Posted image: {image_url}")
                    lim_dict = reddit.auth.limits
                    LOG.info(lim_dict)  # Only update last_post_id if the submission is new
                    last_post_id = submission.id
                else:
                    LOG.info(f"Skipping already posted image: {image_url}")
                    next


    except prawcore.exceptions.NotFound:

        LOG.error("Error: Subreddit not found. Please check the subreddit name in your config file.")


if __name__ == "__main__":
    while True:
        main()
        notify_sleep(sleeptime=1800, reason=f" (pos)")
