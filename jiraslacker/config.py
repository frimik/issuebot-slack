import staticconf
import os

app_config = 'jiraslacker.yaml'
staticconf.YamlConfiguration(app_config)

SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET',
                                      staticconf.read_string('slack.secret'))
JIRA_USERNAME = os.environ.get('JIRA_USERNAME',
                               staticconf.read_string('jira.username'))
JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD',
                               staticconf.read_string('jira.password'))
DATABASE_URL = os.environ.get('DATABASE_URL',
                              staticconf.read_string('db.url'))
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN',
                                 staticconf.read_string('slack.bot_token'))
