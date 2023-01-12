from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from app import db, login_manager


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    oauth_github = db.Column(db.String(100), nullable=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():

            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = generate_password_hash(value)  # we need bytes here (not plain str)
                # need = check_password_hash(password,value)
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

