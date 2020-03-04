# Originally created by Evan. Adaptations made by Brandon Oyer.

import os
import time
from random import randint
from slackclient import SlackClient
from imgurpython import ImgurClient

# Slack environment variables
BOT_ID = os.environ.get("BOT_ID")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
# Imgur environment variables
IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET = os.environ.get("IMGUR_CLIENT_SECRET")

# constants
AT_BOT = "<@" + BOT_ID + ">"
SILLY_COMMAND = "drop the face"
ERASE_COMMAND = "tidy up"
POST_COMMAND = "shitpost"

# instantiate Slack
slack_client = SlackClient(SLACK_BOT_TOKEN)
imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)

def handle_command(command, silly_channel, previous_channel, stamp):
    
    response = "Not sure what you mean. Use *" + SILLY_COMMAND +", *" + ERASE_COMMAND + ", or *" + POST_COMMAND
    
    # Erase messages
    if command.startswith(ERASE_COMMAND):
        channel_list = []
        server_reply = slack_client.api_call("channels.list", exclude_archived=True)
        for ch in [0, 1, 2]:
            channel_list.append(server_reply['channels'][ch]['id'])
        for item in channel_list:
            server_reply = slack_client.api_call("channels.history", channel=item)
            for message in server_reply['messages']:
                if message['user'] == BOT_ID:
                    slack_client.api_call("chat.delete", ts=message['ts'], channel=item, as_user=True)
    
    # Post a picture of Evan
    elif command.startswith(SILLY_COMMAND):
        if stamp != 0:
            slack_client.api_call("chat.delete", ts=stamp, channel=previous_channel, as_user=True)
        response = "http://imgur.com/2AwyQ3b"
        server_reply = slack_client.api_call("chat.postMessage", channel=silly_channel, text=response, as_user=True)
        if server_reply['ok']:
            stamp = server_reply['ts']
            previous_channel = server_reply['channel']
            return stamp, previous_channel

    # Post a meme
    elif command.startswith(POST_COMMAND):
        # Pick a subreddit
        subreddits = ['me_irl', 'memes', 'blackpeopletwitter']
        subreddit_index = randint(0,len(subreddits)-1)
        subreddit = subreddits[subreddit_index]
        print subreddit
        # Get list of shitposts
        shitposts = imgur_client.subreddit_gallery(subreddit)
        # Pick a random one
        number_shitposts = len(shitposts)
        shitpost_index = randint(0, number_shitposts-1)
        random_shitpost = shitposts[shitpost_index]
        # If it's an album, retry until we get an image
        while random_shitpost.is_album or random_shitpost.nsfw:
            shitpost_index = randint(0, number_shitposts-1)
            random_shitpost = shitposts[shitpost_index]
        # Post the image
        slack_client.api_call("chat.postMessage", channel=silly_channel, text=random_shitpost.link, as_user=True)

    else:
        slack_client.api_call("chat.postMessage", channel=silly_channel, text=response, as_user=True)

    return None, None

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                return output['text'], output['channel']
    return None, None

if __name__ == '__main__':
    TIMESTAMP = 0
    previous_channel = 0
    READ_DELAY = 1  # 1 second delay between reading from fire hose
    if slack_client.rtm_connect():
        print("silly-bot connected and running!")
        while True:
            text, channel = parse_slack_output(slack_client.rtm_read())
            if text and channel:
                if AT_BOT in text:
                    command_text = text.split(AT_BOT)[1].strip().lower()
                    TIMESTAMP, previous_channel = handle_command(command_text, channel, previous_channel, TIMESTAMP)
            time.sleep(READ_DELAY)
        print("DISCONNECTED")
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
