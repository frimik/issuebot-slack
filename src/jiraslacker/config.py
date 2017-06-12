# -*- coding: utf-8 -*-
import staticconf
from pkg_resources import resource_filename

default_config_file = resource_filename(__name__, 'defaults.yaml')

def load_config(config_path=default_config_file, defaults='~/.jiraslacker.yaml'):
    staticconf.YamlConfiguration(config_path)

    staticconf.YamlConfiguration(defaults, optional=True)

load_config()

default_host = staticconf.get_string('flask_host')
jira_username = staticconf.get_string('jira_username')
jira_password = staticconf.get_string('jira_password')
database_url = staticconf.get_string('database_url')

DEBUG = False
SQLALCHEMY_DATABASE_URI = database_url
SQLALCHEMY_ECHO = True
THREADS_PER_PAGE = 2
CSRF_ENABLED = True
CSRF_SESSION_KEY = "motherfucker"
SECRET_KEY = "omgcookies"