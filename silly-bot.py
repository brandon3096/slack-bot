#Originally created by Evan Potter. Minor adaptations made by Brandon Oyer. 

import os
import time
from slackclient import SlackClient


# silly-bot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
SILLY_COMMAND = ""

# instantiate Slack
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command):
    response = "Not sure what you mean. Use the *" + SILLY_COMMAND
    if command.startswith(SILLY_COMMAND):
        response = ""
    slack_client.api_call("chat.postMessage", channel="#random", text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                return output['text'], output['channel']
    return None, None


if __name__ == "__main__":
    READ_DELAY = 1  # 1 second delay between reading from fire hose
    if slack_client.rtm_connect():
        print("silly-bot connected and running!")
        while True:
            text, channel = parse_slack_output(slack_client.rtm_read())
            if text and channel:
                if AT_BOT in text:
                    command_text = text.split(AT_BOT)[1].strip().lower()
                    handle_command(command_text)
            time.sleep(READ_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
