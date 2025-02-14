#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
import configparser as config
import csv
import math
import os
import subprocess
import sys
import time

import atproto.exceptions
import dotenv
import prawcore
import requests
from atproto import models
from atproto_client.models import ids

# custom imports
import BlueAuth
import Converter
import GrabSubPosts
import SetupLogging

# Constants and global variables go here
POSTED_IMAGES_CSV = 'posted_images.csv'
CACHE_FOLDER = 'image_cache'
VERSION = '0.1.10'
# this is dumb
LOG = SetupLogging.setup_logger('bluebot', 'bluebot.log')

parser = config.ConfigParser()
parser.read('config.ini')


# Check version from github and compare to current version
def check_version():
    try:
        response = requests.get("https://raw.githubusercontent.com/OwObots/bluebot/main/version.txt", timeout=10)
        if response.status_code == 200:
            version = response.text.strip()
            if version != VERSION:
                LOG.warning(f"New version available: {version}")
            else:
                LOG.info("Running the latest version.")
        else:
            LOG.error("Failed to check for updates.")
    except requests.exceptions.RequestException as e:
        LOG.error(f"Failed to check for updates: {e}")


dotenv.load_dotenv()

# dependencies check
try:
    if sys.platform == 'win32':
        subprocess.check_call(['ffmpeg.exe', '-version'])
    elif sys.platform == 'linux':
        subprocess.check_call(['ffmpeg', '-version'])
except (OSError, IOError):
    LOG.error("ffmpeg is not installed.")
    sys.exit(1)

# Check if required environment variables are set
required_vars = ['APU', 'AP', 'CID', 'CS']
for var in required_vars:
    if var not in os.environ:
        LOG.critical(f"Error: {var} environment variable is not set")
        sys.exit(1)

# client = atproto.Client()
client = BlueAuth.Login(os.environ["APU"], os.environ["AP"])


def send_post_with_labels(client2, text, labels, embed):
    """
    Sends a post with labels using the given client.

    Args:
        client2 (atproto.Client): The client to use for sending the post.
        text (str): The text of the post.
        labels (models.ComAtprotoLabelDefs.SelfLabels): The labels to apply to the post.
        embed (models.AppBskyEmbedImages.Main): The embed content to include in the post.

    Returns:
        models.ComAtprotoRepoCreateRecord.Response: The response from the server.
    """
    return client2.com.atproto.repo.create_record(
        models.ComAtprotoRepoCreateRecord.Data(
            repo=client2.me.did,
            collection=ids.AppBskyFeedPost,
            record=models.AppBskyFeedPost.Record(
                created_at=client2.get_current_time_iso(),
                text=text,
                labels=labels,
                embed=embed
                ),
            )
        )


def duplicate_check(post_id):
    value = False
    with open('posted_images.csv', 'rt', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if post_id in row:
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



def main():
    LOG.info("Starting...")
    reddit = GrabSubPosts.Login(os.environ["CID"], os.environ["CS"])
    
    # this should of been here first lmao
    label = parser.get('bsky', 'label')
    labels = models.ComAtprotoLabelDefs.SelfLabels(
        values=[
            # IDK what to do about nude posts on the subreddit so dm me or smth
            models.ComAtprotoLabelDefs.SelfLabel(val=label),
            ]
        )
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
        sub = GrabSubPosts.get_subreddit(os.environ["CID"], os.environ["CS"])
        with open(POSTED_IMAGES_CSV, 'r') as csvfile:
            reader = csv.reader(csvfile)
            posted_images = set(row[0] for row in reader)
        results = []
        new_posts_found = False
        for submission in sub.hot():
            if len(results) >= limit:  # Stop when we reach the limit
                continue
            if 'imgur.com' in submission.url:
                LOG.info(f"Skipping Imgur post: {submission.url}")
                # TODO: add support for imgur posts (album, gallery, etc)
                continue
            post_id = submission.id
            if not submission.stickied and not submission.is_self and submission.url.endswith(
                    ('.jpg', '.png', '.gif', '.bmp')
                    ):
                results.append(submission)
                LOG.info(f"{submission.title} ({submission.author.name})")
                image_url = submission.url
                if not duplicate_check(post_id):
                    # this is separate form the below because we want to convert the gif to a mp4 and then post it
                    if submission.url.endswith('.gif'):
                        image_data = requests.get(image_url, timeout=60).content
                        # image_size = len(image_data)
                        cached_image_data, mime_type, height, width = Converter.ImgPrep(image_data)
                        upload = client.upload_blob(image_data)
                        ratio_as_bsky = models.AppBskyEmbedDefs.AspectRatio(height=height, width=width)
                        images = models.AppBskyEmbedVideo.Main(alt='', video=upload.blob, aspect_ratio=ratio_as_bsky)
                        send_post_with_labels(
                            client, submission.title + " (u/" + submission.author.name + ")", labels, images
                            )
                        with open(POSTED_IMAGES_CSV, 'a') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow([post_id])
                        LOG.info(f"Posted image: {image_url}")
                        lim_dict = reddit.auth.limits
                        LOG.info(lim_dict)  # Only update last_post_id if the submission is new
                        last_post_id = submission.id
                        
                        # upload = client.send_video(text=submission.title + " (u/" + submission.author.name + ")",
                        # video=image_data, video_alt='',)
                    else:
                        image_data = requests.get(image_url, timeout=60).content
                        image_size = len(image_data)
                        max_size = 976560
                        if image_size <= max_size:
                            # TODO: add ocr
                            # client.send_image(
                            #    text=submission.title + " (u/" + submission.author.name + ")" + "  " +
                            #    submission.source,
                            #    image=image_data,
                            #    image_alt='', )
                            cached_image_data, mime_type, height, width = Converter.ImgPrep(image_data)
                            ratio_as_bsky = models.AppBskyEmbedDefs.AspectRatio(height=height, width=width)
                            upload = client.upload_blob(cached_image_data)
                            images = [
                                models.AppBskyEmbedImages.Image(alt='', image=upload.blob, aspect_ratio=ratio_as_bsky)]
                            embed = models.AppBskyEmbedImages.Main(images=images)
                            send_post_with_labels(
                                client, submission.title + " (u/" + submission.author.name + ")", labels,
                                embed
                                )
                            with open(POSTED_IMAGES_CSV, 'a') as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow([post_id])
                            LOG.info(f"Posted image: {image_url}")
                            lim_dict = reddit.auth.limits
                            LOG.info(lim_dict)  # Only update last_post_id if the submission is new
                            last_post_id = submission.id
                        else:
                            LOG.info(f"Resizing image because it's too big: {image_url}")
                            compressed_image_data = Converter.compress_image(image_data, image_url)
                            compressed_image_size = len(compressed_image_data)
                            if compressed_image_size > max_size:
                                LOG.info(f"Skipping image because it's still too big after compression: {image_url}")
                                with open(POSTED_IMAGES_CSV, 'a') as csvfile:
                                    writer = csv.writer(csvfile)
                                    writer.writerow([post_id])
                                continue
                            else:
                                cached_image_data, mime_type, height, width = Converter.ImgPrep(compressed_image_data)
                                ratio_as_bsky = models.AppBskyEmbedDefs.AspectRatio(height=height, width=width)
                                upload = client.upload_blob(cached_image_data)
                                images = [
                                    models.AppBskyEmbedImages.Image(
                                        alt='', image=upload.blob, aspect_ratio=ratio_as_bsky
                                        )]
                                embed = models.AppBskyEmbedImages.Main(images=images)
                                send_post_with_labels(
                                    client, submission.title + " (u/" + submission.author.name + ")",
                                    labels,
                                    embed
                                    )
                                with open(POSTED_IMAGES_CSV, 'a') as csvfile:
                                    writer = csv.writer(csvfile)
                                    writer.writerow([post_id])
                                LOG.info(f"Posted compressed image: {image_url}")
                                lim_dict = reddit.auth.limits
                                LOG.info(lim_dict)
                                last_post_id = submission.id
                                LOG.info(f"Image size: {image_size} bytes")
                else:
                    LOG.info(f"Skipping already posted image: {image_url}")
                    continue
    
    except prawcore.exceptions.NotFound:
        LOG.error("Error: Subreddit not found. Please check the subreddit name in your config file.")


if __name__ == "__main__":
    while True:
        try:
            check_version()
            main()
            notify_sleep(sleeptime=36000, reason=" (no new posts)")
        except Exception as at:
            LOG.error(f"Error: {at}")
            if 'ratelimit-reset' in str(at):
                # reset is in unix time
                limit, remaining, reset = client.get_rate_limit()
                current_time = int(time.time())
                sleep_time = max(int(reset) - current_time, 0)
                LOG.info(f"Rate limit reached. Limit: {limit}, Remaining: {remaining}, Reset: {reset}")
                LOG.info(f"Sleeping for {sleep_time} seconds.")
                notify_sleep(sleeptime=sleep_time, reason=" (rate limit reached)")
            # notify_sleep(sleeptime=int(reset), reason=" (rate limit reached)")
            else:
                notify_sleep(sleeptime=36000, reason=f" {at}")
