from gevent import monkey; monkey.patch_all()  # noqa
import os
from flask import Flask, request, Response
import staticconf
import click

app_config = 'eajiraslacker.yaml'
staticconf.YamlConfiguration(app_config)

SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET',
                                      staticconf.read_string('slack.secret'))
app = Flask(__name__)


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
    return Response(), 200


@click.command()
@click.option('--host', default='127.0.0.1',
              help='Interface to listen on. Use 0.0.0.0 for all interfaces.',
              metavar='<host>')
def serve(host):
    app.run(debug=True, host=host)
