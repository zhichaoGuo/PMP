# -*- encoding: utf-8 -*-
import os, random, string


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')
    SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))
    # SQLALCHEMY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    # LDAP
    LDAP_HOST = "192.168.0.164"
    LDAP_PORT = 389
    LDAP_USER_OBJECT_FILTER = "(&(objectclass=Person)(sAMAccountName=%s))"
    LDAP_BASE_DN = "ou=htek,dc=htek,dc=org"
    LDAP_USERNAME = "cn=ldapadmin,ou=htek,dc=htek,dc=org"
    LDAP_PASSWORD = "LDap123"
    # LOGGER


class ProductionConfig(Config):
    DEBUG = False
    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
