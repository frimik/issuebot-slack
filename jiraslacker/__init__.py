from gevent import monkey; monkey.patch_all()  # noqa
from flask import Flask, request, Response
import click
from config import SLACK_WEBHOOK_SECRET
from slacker import JiraServer, JiraSlacker
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

logger.info('Starting up Flask...')


class FlaskApp(Flask):
    def __init__(self, import_name):
        super(FlaskApp, self).__init__(import_name)
        JiraServer.init_caches()

app = FlaskApp(__name__)


@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'


@app.route('/slack/jira', methods=['POST'])
def inbound():
    if request.form.get('token') == SLACK_WEBHOOK_SECRET:
        channel = request.form.get('channel_name')
        username = request.form.get('user_name')
        text = request.form.get('text')
        inbound_message = username + " in " + channel + " says: " + text
        click.echo(inbound_message)
        response = JiraSlacker.process(text)
    return Response(), 200


@click.command()
@click.option('--host', default='127.0.0.1',
              help='Interface to listen on. Use 0.0.0.0 for all interfaces.',
              metavar='<host>')
def serve(host):
    app.run(debug=True, host=host)
