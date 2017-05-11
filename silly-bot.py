import os
import time
from slackclient import SlackClient

# silly-bot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
SILLY_COMMAND = "drop the face"
ERASE_COMMAND = "tidy up"

# instantiate Slack
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, silly_channel, prev_channel, stamp):
    response = "Not sure what you mean. Use the *" + SILLY_COMMAND
    if command.startswith(ERASE_COMMAND):
        channel_list = []
        server_reply = slack_client.api_call("channels.list", exclude_archived=True)
        #print server_reply['channels'][0]['id']
        #print len(server_reply['channels'])
        #for ch in server_reply['channels']:
        for ch in [0, 1, 2]:
            channel_list.append(server_reply['channels'][ch]['id'])
        for item in channel_list:
            print item
            break
            server_reply = slack_client.api_call("channels.history", channel=item)
            for message in server_reply['messages']:
                if message['user'] == BOT_ID:
                    slack_client.api_call("chat.delete", ts=message['ts'], channel=item, as_user=True)
    if command.startswith(SILLY_COMMAND):
        #print silly_channel
        if stamp != 0:
            slack_client.api_call("chat.delete", ts=stamp, channel=prev_channel, as_user=True)
        response = "http://imgur.com/2AwyQ3b"
        server_reply = slack_client.api_call("chat.postMessage", channel=silly_channel, text=response, as_user=True)
        if server_reply['ok']:
            stamp = server_reply['ts']
            delete_channel = server_reply['channel']
            return stamp, delete_channel
    return 0, 0

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                return output['text'], output['channel']
    return None, None

if __name__ == '__main__':
    TIMESTAMP = 0
    delete_channel = 0
    READ_DELAY = 1  # 1 second delay between reading from fire hose
    if slack_client.rtm_connect():
        print("silly-bot connected and running!")
        while True:
            text, channel = parse_slack_output(slack_client.rtm_read())
            if text and channel:
                if AT_BOT in text:
                    command_text = text.split(AT_BOT)[1].strip().lower()
                    TIMESTAMP, delete_channel = handle_command(command_text, channel, delete_channel, TIMESTAMP)
            time.sleep(READ_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
