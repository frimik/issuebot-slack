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

    def process(self):
        return self.parse_command()

    def list_servers(self, args):
        servers = [str(s) for s in JiraServer.server_list()]
        return SlackFormatter.object_to_message(servers)

    def add_server(self, args):
        server = JiraServer(
            args.server_url,
        ).save()
        return SlackFormatter.object_to_message("Added server: {server}".format(server=server))

    def parse_command(self):
        return self.parse_args(shlex.split(self.text))

    def parse_args(self, argv):
        parser = SlashCommand.get_parser(self.command)
        try:
            args = parser.parse_args(argv)
        except SystemExit:
            return False

        if 'func' in args:
            return args.func(self, args)
        else:
            help_string = parser.format_help()
            return {'response_type': 'ephemeral',
                    'text': help_string}

    @staticmethod
    def get_parser(prog='/jira'):
        parser = argparse.ArgumentParser(prog=prog)
        subparsers = parser.add_subparsers()

        list_group = subparsers.add_parser('list')
        add_group = subparsers.add_parser('add')
        update_group = subparsers.add_parser('update')
        delete_group = subparsers.add_parser('delete')

        subparsers = list_group.add_subparsers()
        server_list = subparsers.add_parser('server', aliases=['servers'])
        server_list.set_defaults(func=SlashCommand.list_servers)

        subparsers = add_group.add_subparsers()
        server_add = subparsers.add_parser('server')
        server_add.add_argument('--server-url')
        server_add.add_argument('--user', '--username')
        server_add.add_argument('--pass', '--password')
        server_add.set_defaults(func=SlashCommand.add_server)

        return parser


class JiraSlacker(object):
    """Docstring for JiraSlacker. """

    def __init__(self):
        """TODO: to be defined1. """

    @classmethod
    def process_request(cls, request):
        response = SlashCommand(request.form).process()
        if not response:
            return cls.lookup_issues(request)
        return response

    @classmethod
    def lookup_issues(cls, request):
        greenlet = gevent.spawn(cls._process, request.form.get('text'))
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
