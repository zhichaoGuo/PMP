import datetime

from werkzeug.security import generate_password_hash

from app import db


class Model(db.Model):  # 型号表
    __tablename__ = 'Model'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return str(self.name)


class Way(db.Model):  # 激励策略表
    __tablename__ = 'Way'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(64), unique=True)
    start_time = db.Column(db.DateTime(), default=datetime.datetime.now())
    status = db.Column(db.Boolean(), default=False)


class Node(db.Model):  # 激励节点表
    __tablename__ = 'Node'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    way_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.String(64))


class Record(db.Model):  # 销售记录表
    __tablename__ = 'Record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    sale_time = db.Column(db.DateTime(), default=datetime.datetime.now())


class Detail(db.Model):  # 销售明细表
    __tablename__ = 'Detail'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_id = db.Column(db.Integer, nullable=False)
    model_id = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    sale_time = db.Column(db.DateTime(), default=datetime.datetime.now())
    sale_number = db.Column(db.Integer, nullable=False)