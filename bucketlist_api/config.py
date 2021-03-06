"""Script define the various app configuration."""

import os


class Config(object):
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    ERROR_404_HELP = False
    SECRET_KEY = 'randomthoughscomingtomymind'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    DEFAULT_PER_PAGE = 20
    MAX_PER_PAGE = 100


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'production-url')


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'bucketlist.sqlite'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)


class TestConfig(Config):
    """Test configuration."""
    ENV = 'test'
    TESTING = True
    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
