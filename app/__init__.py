import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_bootstrap import Bootstrap
from flask_login import LoginManager


db = SQLAlchemy()
# login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    # login_manager.init_app(app)


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



def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app