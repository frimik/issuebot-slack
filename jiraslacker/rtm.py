from __future__ import print_function
import logging
from slackclient import SlackClient
from slacker import JiraSlacker
import gevent

from config import SLACK_BOT_TOKEN
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def main():

    slack = SlackClient(SLACK_BOT_TOKEN)
    if slack.rtm_connect(with_team_state=False, auto_reconnect=True):
        while slack.server.connected is True:
            events = slack.rtm_read()
            print(events)
            for event in events:
                if event.get('type') == 'message' and event.get('subtype') != 'bot_message':
                    response = JiraSlacker._process(event.get('text'))
                    channel = event.get('channel')
                    if response:
                        print(response)
                        slack.rtm_send_message(channel, response.get('text'))
            gevent.sleep(1)

    else:
        print("Connection failed")


if __name__ == "__main__":
    main()
