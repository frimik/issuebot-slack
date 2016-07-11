from __future__ import print_function
from jira import JIRA
from config import JIRA_USERNAME, JIRA_PASSWORD, DATABASE_URL
import dataset
import re
import logging
from slackformatter import SlackFormatter

logger = logging.getLogger(__name__)

db = dataset.connect(DATABASE_URL)


class JiraServer(JIRA):

    __server_list = []
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
        self.jira = super(JiraServer, self).__init__(
            server, basic_auth=self.basic_auth
        )

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           self.server)

    def __repr__(self):
        return '<jiraslacker %s(%s) at %s> Project Keys: %s' % (
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
        return cls.__server_list


class JiraSlacker(object):

    """Docstring for JiraSlacker. """

    def __init__(self):
        """TODO: to be defined1. """

    @classmethod
    def process(cls, text):
        issue_keys = re.findall(r'\b(([A-Z]{1,4})\-(\d+))\b', text)
        response_type = 'ephemeral'
        if text.endswith('public') or text.startswith('public'):
            response_type = 'in_channel'
        else:
            response_type = 'ephemeral'
        logger.info('Incoming issue keys: %s', issue_keys)
        issues = []
        for (issue_key, project_key, issue_num) in issue_keys:
            matching_jira_servers = [s for s in JiraServer.server_list()
                                     if project_key in s.project_keys]
            logging.info('Matching JIRA servers: %s', matching_jira_servers)
            for server in matching_jira_servers:
                issue = server.issue(
                    issue_key, fields='summary,status,issuetype'
                )
                issues.append(issue)
                issue_info = '{0} ({1}): *{2}* {3} - {4}'.format(
                    issue, issue.fields.issuetype, issue.fields.status,
                    issue.fields.summary, issue.permalink()
                )
                logging.info(issue_info)

        return SlackFormatter(
            issues,
            response_type=response_type).format_response()


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
