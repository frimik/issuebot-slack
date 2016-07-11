from gevent import monkey; monkey.patch_all()  # noqa
from flask import Flask
import click
from slacker import JiraServer
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

logger.info('Starting up Flask...')


class FlaskApp(Flask):
    def __init__(self, import_name):
        super(FlaskApp, self).__init__(import_name)
        JiraServer.init_caches()

app = FlaskApp(__name__)
import jiraslacker.views  # noqa


@click.command()
@click.option('--host', default='127.0.0.1',
              help='Interface to listen on. Use 0.0.0.0 for all interfaces.',
              metavar='<host>')
def serve(host):
    app.run(debug=True, host=host,
            extra_files=['jiraslacker.yaml'])
