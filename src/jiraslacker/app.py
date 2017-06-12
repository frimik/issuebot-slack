from gevent import monkey;

monkey.patch_all()  # noqa

import gevent
import os
from flask import Flask
from .models import db, JiraServer
from .config import default_config_file
import click
import logging
from .remoteconsole import start_console

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FlaskApp(Flask):
    def __init__(self, import_name):
        super(FlaskApp, self).__init__(import_name)

    def init_caches(self):
        JiraServer.init_caches()


def create_app():
    app = FlaskApp(__name__)
    db.init_app(app)
    return app


app = create_app()
from . import views

db.init_app(app)


@click.command()
@click.option('--host', default='127.0.0.1', help='Interface to listen on. Use 0.0.0.0 for all interfaces.',
              metavar='<host>')
@click.option('--config', default=default_config_file, help='Path to a configuration file', metavar='<config>')
def run(host, config):
    debug = False
    if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        logger.info('Flask main child process starting ...')
        with app.app_context():
            db.create_all()
            jira = JiraServer('https://jira.atlassian.com').save()
            servers_in_db = JiraServer.query.all()
            logger.info("Servers in DB: %s", servers_in_db)
            app.init_caches()
            logger.info("Cached servers are now: %s", JiraServer.server_list())
    else:
        logger.info('Flask parent process starting ...')

    start_console()

    flask_web = gevent.spawn(app.run, debug=debug, host=host,
                             extra_files=[config])
    flask_web.join()
    # app.run(debug=debug, host=host, extra_files = [config])
