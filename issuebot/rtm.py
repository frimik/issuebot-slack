#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import gevent
import logging
import json
import re
from slackclient import SlackClient
from slackclient.channel import Channel
from slacker import IssueBot
from config import SLACK_BOT_TOKEN, BOT_INFORMATION
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Pre-built "nice strings" for jira server info ... used in the *info* command.
# Side effect also that the jira server list gets pre-cached now instead of on-demand.


def jsonFormat(obj):
    return json.dumps(obj, sort_keys=True,
                      indent=4, separators=(',', ': '))


jiraServerInfos = []
for server in IssueBot.server_list():
    key_string = ', '.join('`{0}`'.format(key)
                           for key in server.project_keys)
    jiraServerInfo = "Server: {0} (User: `{1}`), Keys: {2}".format(
        server.server, server.username, key_string)
    print(jiraServerInfo)
    jiraServerInfos.append(jiraServerInfo)


class Bot(object):

    def __init__(self, slack_client):
        self.slack = slack_client

    def respond_hello(self, event_channel):
        self.slack.server.rtm_send_message(
            event_channel,
            ("Hi! I'm a bot which pick up any capitalized mention of JIRA Issues"
             " (`ABC-123`) and respond with JIRA Information (in a thread)."
             " Available commands: `hello`."
             " I have access to the following JIRAs and project keys:\n"
             "{0}.\n"
             "{1}"
             ).format(
                "\n".join(jiraServerInfos),
                BOT_INFORMATION
            )
        )


def main():

    # Quick hacky RTM (Real Time Message) API test when I realized the slashcommand route is
    # both annoying in terms of Internet=>corp restrictions
    # as well as not actually "helpful". If possible, an integration should help a user
    # implicitly. Ie, helpfully add value without the user having to *explicitly* ask for it.
    # That's why it makes sense to go the "listen-to-all-conversations-route" primarily, and
    # let's add some extra value with Slash Commands and possibly dialogue integrations later.
    # Currently only supports JIRA. Should add support for:
    # gitlab (issues, pull requests (issue# matching) and commits, branches, tags (url/sha/etc-matching))
    # github? (not right now, we don't have any github enterprise left)
    slack = SlackClient(SLACK_BOT_TOKEN)
    bot = Bot(slack)
    if slack.rtm_connect(with_team_state=False, auto_reconnect=True):
        while slack.server.connected is True:

            # Read next batch (list) of events from the RTM API:
            events = slack.rtm_read()

            for event in events:
                # TODO ship each event into all registered handlers?
                event_type = event.get('type')
                event_subtype = event.get('subtype')
                event_text = event.get('text')
                event_channel = event.get('channel')
                event_ts = event.get('ts')
                event_thread_ts = event.get('thread_ts')
                hidden = event.get('hidden')

                logger.debug("Incoming event, type: %s, json:\n%s",
                             event_type, jsonFormat(event))

                # React to non-bot, non-hidden messages only
                if event_type == 'message' and event_subtype != 'bot_message' and not hidden:

                    # Decide whether to respond to an unthreaded message or an already-threaded message
                    if event_thread_ts:
                        # The message was already in a thread
                        thread = event_thread_ts
                        # Do not broadcast, keep it in thread only
                        reply_broadcast = False
                    else:
                        # The message is not (yet) on a thread
                        thread = event_ts
                        # Do not broadcast, keep it in thread only (this used to be True - but too noisy? (make it a per-channel option later?))
                        reply_broadcast = False

                    event_words = event_text.split()
                    if len(event_words) == 2:
                        if event_words[0] == "<@{0}>".format(slack.server.userid):
                            # I'm mentioned
                            if event_words[1] == "leave":
                                # And I'm asked to leave.
                                # TODO impossible, bots cannot leave channels!
                                # The only API available right is a kött-API:
                                # slack.rtm_send_message("#slack-admins", "Please kick me from {!0s}".format(event_channel)))
                                continue
                            elif event_words[1] == "ignore":
                                # I'm asked to ignore this channel.
                                slack.rtm_send_message(
                                    event_channel, "(Not implemented yet) - Ok, I will ignore this channel from now on. Re-enable by telling me to `listen`.")
                                continue
                            elif event_words[1] == "listen":
                                # I'm asked to pay attention to this channel (again).
                                slack.rtm_send_message(
                                    event_channel, "(Not implemented yet) - I will listen for issues from now on. (Commands: `ignore`, `listen`)")
                                continue
                            elif event_words[1] in ["hello", "help", "info"]:
                                # I support these projects ...
                                bot.respond_hello(event_channel)
                                continue

                    # No other unique event matches, go ahead and process the message. If there is something interesting
                    # a response will be sent.
                    response = IssueBot._process(event_text)
                    if response:
                        print("Response: {0!s}".format(jsonFormat(response)))
                        slack.rtm_send_message(event_channel, response.get('text'),
                                               thread=thread, reply_broadcast=reply_broadcast)

            gevent.sleep(1)

    else:
        print("Connection failed")


if __name__ == "__main__":
    main()
