from flask_sqlalchemy import SQLAlchemy
from jira import JIRA
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


# Define a JiraServer model
class JiraServer(JIRA, Base):
    __tablename__ = 'jiraservers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    server = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))

    # class cache
    __server_list = []
    __longest_project_key = 1

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
            server, basic_auth=self.basic_auth)

    def __str__(self):
        return '%s (Username: %s)' % (self.server, self.username)

    def __repr__(self):
        return '<jiraslacker %s(%s) at %s> (Username: %s) Project Keys: %s' % (
            self.__class__.__name__,
            self.server,
            self.username,
            id(self),
            self.project_keys
        )

    def save(self):
        db.session.add(self)
        logger.info('Persisting server to database: %s', self)
        db.session.commit()
        return self

    def cache_project_keys(self):
        logger.info("Caching project keys on server: %s", self.server)
        projects = self.projects()
        keys = sorted([project.key for project in projects])
        self.project_keys = keys
        self.update_project_key_length(max(len(s) for s in keys))
        logger.info("Server: %s, Keys: %s", self.server, self.project_keys)

    def update_project_key_length(self, keylen):
        klass = self.__class__
        max_len = max(self.longest_project_key(), keylen)
        klass.__longest_project_key = max_len
        logger.debug("Longest JIRA project key length now: %d", max_len)

    @classmethod
    def longest_project_key(cls):
        return cls.__longest_project_key

    @classmethod
    def from_db_dict(cls, db_dict):
        _server_dict = {}
        for key in cls.__columns:
            _server_dict[key] = db_dict[key]

        return cls(**_server_dict)

    @classmethod
    def init_caches(cls):
        """Initialize server and project key caches from the database"""
        logger.info("init_caches() called")
        _servers = cls.cache_server_list()
        for _s in _servers:
            _s.cache_project_keys()

    @classmethod
    def cache_server_list(cls):
        logger.info("Caching server list...")
        _server_list = []
        for _server in cls.query.all():
            logger.info("Server: %s", _server)
            _server_list.append(_server)

        cls.__server_list = _server_list
        return cls.__server_list

    @classmethod
    def server_list(cls):
        return cls.__server_list
