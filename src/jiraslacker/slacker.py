from __future__ import print_function
import gevent
import re
import logging
from .models import JiraServer
from .slackformatter import SlackFormatter
from time import sleep
from random import randrange
import shlex
import argparse

logger = logging.getLogger(__name__)


class SlashCommand(object):
    """"
    We're looking at slash commands coming in like:
    /slack Let's look up some JIRAs shall we? ... JIRA-123 JIRA-456 JIRA-789 https://jira.example.com/uo/browse/FOO-123
    /slack server add https://jira.example.com/ user[name]:username pass[word]:password description:foobar
    /slack servers?(?: list)?
    /slack server delete [id]
    """

    def __init__(self, form_dict):
        self.token = ""
        self.team_id = ""
        self.team_domain = ""
        self.enterprise_id = ""
        self.enterprise_name = ""
        self.channel_id = ""
        self.channel_name = ""
        self.user_id = ""
        self.user_name = ""
        self.command = ""
        self.text = ""
        self.response_url = ""

        for k, v in form_dict.items():
            setattr(self, k, v)

    def parse_command(self):
        self.parse_command(self.text)

    @staticmethod
    def parse_command(text):
        SlashCommand.parse_args(shlex.split(text))

    @staticmethod
    def server_list():
        return JiraServer.server_list()

    @staticmethod
    def parse_args(argv):
        parser = SlashCommand.get_parser()
        args = parser.parse_args(argv)
        if 'command' in args:
            args.command()

    @staticmethod
    def get_parser():
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers()

        server_parser = subparsers.add_parser('server', aliases=['servers'])
        server_subparser = parser.add_subparsers()
        server_subparser.add_parser('list')
        server_subparser.set_defaults(command=SlashCommand.server_list)


class JiraSlacker(object):
    """Docstring for JiraSlacker. """

    def __init__(self):
        """TODO: to be defined1. """

    @classmethod
    def process_request(cls, request):
        slash_command = SlashCommand(request.form)

        greenlet = gevent.spawn(cls._process, text)
        gevent.joinall([greenlet], timeout=3)
        return greenlet.value

    @classmethod
    def process_issue_key(cls, issue_key):
        if randrange(0, 2) == 1:
            sleep(6)
        issues = []
        (issue_key, project_key, issue_num) = list(issue_key)
        matching_jira_servers = [s for s in JiraServer.server_list()
                                 if project_key in s.project_keys]
        logger.debug('Matching JIRA servers: %s', matching_jira_servers)
        for server in matching_jira_servers:
            issue = server.issue(
                issue_key, fields='summary,status,issuetype'
            )
            issues.append(issue)
            issue_info = '{0} ({1}): *{2}* {3} - {4}'.format(
                issue, issue.fields.issuetype, issue.fields.status,
                issue.fields.summary, issue.permalink()
            )
            logger.info("Issue: %s", issue_info)
        return (issues)

    @classmethod
    def _process(cls, text):
        logger.debug("Incoming text: %s", text)

        rx = r"\b(([A-Z]{1,%d})\-(\d+))\b" % JiraServer.longest_project_key()
        issue_keys = re.findall(rx, text)
        response_type = 'ephemeral'  # default ephemeral response type
        if text.strip().endswith('public') or text.strip().startswith('public'):
            response_type = 'in_channel'

        logger.info('Incoming issue keys: %s', issue_keys)
        issues = []

        greenlets = [gevent.spawn(cls.process_issue_key, i) for i in issue_keys]

        finished = gevent.joinall(greenlets, timeout=2)
        for greenlet in finished:
            issues.extend(greenlet.value)

        slack_formatted = SlackFormatter(
            issues,
            response_type=response_type).format_response()
        return slack_formatted

    @classmethod
    def respond_later(cls, greenlets):
        issues = []
        later = gevent.joinall(greenlets, timeout=10)
        for greenlet in later:
            issues.extend(greenlet.value)

        gevent.spawn(cls.callback_respond, issues)

    @classmethod
    def callback_respond(cls, slack_formatted):
        # TODO Call back to Slack here
        return

    @classmethod
    def process(cls, text):
        greenlet = gevent.spawn(cls._process, text)
        gevent.joinall([greenlet], timeout=3)
        return greenlet.value


def main():
    jira = JiraServer('https://jira.dice.se',
                      JIRA_USERNAME, JIRA_PASSWORD)
    jira.save()

    jira.cache_project_keys()
    projects = jira.projects()

    keys = sorted([project.key for project in projects])
    print(keys)


#    issue = jira.issue('UO-53')
#
#    import re
#    ea_comments = [
#        comment for comment in issue.fields.comment.comments
#        if re.search(r'@ea.com$', comment.author.emailAddress)]
#
#    click.echo(ea_comments)


if __name__ == "__main__":
    main()
