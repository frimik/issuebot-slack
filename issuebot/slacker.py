from __future__ import print_function
import gevent
import random
from jira import JIRA
from config import DATABASE_URL, ISSUE_SERVERS
import dataset
import re
import logging
from slackformatter import SlackFormatter

logger = logging.getLogger(__name__)

db = dataset.connect(DATABASE_URL)


class JiraServer(JIRA):

    __server_list = []
    __init_done = False
    __table_name = 'servers'
    __table = db[__table_name]
    __columns = ['server', 'username', 'password']

    """JIRA Server"""

    def __init__(self, server, username=None, password=None):
        """TODO: to be defined1. """
        self.server = server
        self.basic_auth = None
        self.username = username
        self.password = password
        self.project_keys = []

        if username is not None and password is not None:
            self.basic_auth = (self.username, self.password)
        self.jira = super(self.__class__, self).__init__(
            server, basic_auth=self.basic_auth
        )

    def __str__(self):
        return 'Server: {0!s}, Keys: {1!s}'.format(self.server, map(str, self.project_keys))

    def __repr__(self):
        return '<issuebot %s(%s) at %s> Project Keys: %s' % (
            self.__class__.__name__,
            self.server,
            id(self),
            self.project_keys
        )

    def save(self):
        return self.__table.upsert(
            dict(
                server=self.server, username=self.username,
                password=self.password,
            ),
            ['server', 'username']
        )

    def cache_project_keys(self):
        logger.info("Caching project keys on server: %s", self.server)
        projects = self.projects()
        keys = sorted([project.key for project in projects])
        self.project_keys = keys
        logger.info("Server: %s, Keys: %s", self.server, self.project_keys)

    @classmethod
    def from_db_dict(cls, db_dict):
        _server_dict = {}
        for key in cls.__columns:
            _server_dict[key] = db_dict[key]

        return cls(**_server_dict)

    @classmethod
    def init_caches(cls):
        """Initialize server and project key caches"""
        logger.info("init_caches() called")
        _servers = cls.cache_server_list()
        for _s in _servers:
            _s.cache_project_keys()
        cls.__init_done = True

    @classmethod
    def cache_server_list(cls):
        logger.info("Caching server list...")
        _server_list = []
        for _server in cls.__table.all():
            _server_list.append(cls.from_db_dict(_server))

        cls.__server_list = _server_list
        return cls.__server_list

    @classmethod
    def server_list(cls):
        if not cls.__init_done:
            cls.init_caches()
        return cls.__server_list


class SlashCommand(object):
    """SlashCommand: https://api.slack.com/slash-commands """

    def __init__(self):
        self.command = None
        self.channel_id = None
        self.channel_name = None
        self.user_name = None
        self.user_id = None
        self.text = None
        self.response_url = None
        self.trigger_id = None

    @classmethod
    def from_request(cls, request):
        slash_command = SlashCommand()
        for parameter in [
            'command',
            'channel_id',
            'channel_name',
            'user_name',
            'user_id',
            'text',
            'response_url',
            'trigger_id',
        ]:
            setattr(slash_command, parameter, request.form.get(parameter))

        return slash_command

    def process(self):
        """
        If a formatted response can be gotten within 2 seconds - return an immediate response.
        If not, return an empty response here. A delayed response will follow.
        """
        # Spawn the async process task
        task = gevent.spawn(IssueBot._process, self.text)
        # Wait 2 seconds:
        greenlets = gevent.wait([task], timeout=2)
        if greenlets:
            return greenlets[0].value
        else:
            # Time out, start a delayed response and return nothing (200)
            logger.info(
                "Timed out (2 seconds) - will send a delayed response.")
            gevent.spawn(self._process_delayed, task)
            return

    def _process_delayed(self, task):
        greenlets = gevent.joinall([task])
        for greenlet in greenlets:
            response = greenlet.value
            logger.info("Delayed response: %s", response)
            logger.info("Response url: %s", self.response_url)

        return


class IssueBot(object):

    """Docstring for IssueBot. """

    def __init__(self):
        """ not much here """

    @classmethod
    def process_issue_key(cls, issue_key):
        gevent.sleep(random.randrange(0, 3))
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
            logger.info(issue_info)

        return(issues)

    @classmethod
    def server_list(cls):
        return JiraServer.server_list()

    @classmethod
    def _process(cls, text):
        """ Returns a formatted json response containing all matching JIRA issue statuses """

        # Return if no text coming in
        if not text:
            return

        issue_keys = re.findall(r'\b(([A-Z]{1,10})\-(\d+))\b', text)
        response_type = 'ephemeral'

        logger.info('Incoming issue keys: %s', issue_keys)
        issues = []
        greenlets = []
        for issue_key in issue_keys:
            logger.info("Spawning lookup for %s", issue_key)
            greenlets.append(gevent.spawn(cls.process_issue_key, issue_key))

        objs = gevent.joinall(greenlets)
        for obj in objs:
            if obj.value:
                logger.debug("Issue result: %s", obj.value)
                issues.extend(obj.value)

        if issues:
            return SlackFormatter(
                issues,
                response_type=response_type).format_response()

        return None


def main():

    for server in ISSUE_SERVERS:
        jira = JiraServer(server['server'],
                          server['username'], server['password'])
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
