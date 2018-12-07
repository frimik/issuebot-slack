from staticconf import YamlConfiguration, read_string, read_list
import os

app_config = 'issuebot.yaml'
YamlConfiguration(app_config)


ISSUE_SERVERS = read_list('servers')

SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET',
                                      read_string('slack.secret'))

DATABASE_URL = os.environ.get('DATABASE_URL',
                              read_string('db.url'))
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN',
                                 read_string('slack.bot_token'))
BOT_INFORMATION = os.environ.get('BOT_INFORMATION',
                                 read_string('bot.information'))
