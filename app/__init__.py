import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, session, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_simpleldap import LDAP
from flask_login import LoginManager, logout_user


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'home.login'


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    new = datetime.datetime.now()
    username = str(User.query.get(int(user_id)))
    user = User.query.filter_by(username=username).first()
    if user:
        old = user.last_login_time
        # 登录超时 3600s -> 1h
        if (new - old).seconds > 3600:
            user.is_login = False
            db.session.add(user)
            db.session.commit()
            session.clear()
            logout_user()
            current_app.logger.info('%s online time out, auto logout,last login time is:%s' % (username, old))
            return None
        return User.query.get(int(user_id))
    return User.query.get(int(user_id))


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    app.ldap = LDAP(app)


def register_blueprints(my_app):
    from app.admin import admin
    from app.home import home
    from app.excitation import excitation
    my_app.register_blueprint(admin)
    my_app.register_blueprint(home)
    my_app.register_blueprint(excitation)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:
            print('> Error: DBMS Exception: ' + str(e))
            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///../DataBase/db.sqlite3'
            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def configure_logger(my_app):
    my_app.logger.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s][%(module)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")
    handler = TimedRotatingFileHandler("./Log/flask.log", when="D", interval=1, backupCount=15, encoding="UTF-8",
                                       delay=False, utc=True)
    my_app.logger.addHandler(handler)
    handler.setFormatter(formatter)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    configure_logger(app)
    return app
