import datetime

import sqlalchemy
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

    def turn_json(self):
        data = {
            "id": self.id,
            "way_id": self.way_id,
            "price": self.price,
            "percentage": self.percentage
        }
        return data


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
    sale_time = db.Column(db.Date, default=datetime.date.today())
    sale_number = db.Column(db.Integer, nullable=False)


class Global(db.Model):  # 全局配置表
    __tablename__ = 'Global'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(64), nullable=False)


class DataBaseUtils:
    @staticmethod
    def add_model(model_name):
        try:
            new = Model(name=model_name)
            db.session.add(new)
            db.session.commit()
            return 200, 'OK'
        except sqlalchemy.exc.IntegrityError:
            return 400, '型号已存在!'

    @staticmethod
    def delete_model(model_id):  # Todo: 删除型号下所有的激励策略及节点
        try:
            delete = Model.query.filter_by(id=model_id).first()
            if delete:
                db.session.delete(delete)
                db.session.commit()
                return 200, 'OK'
            else:
                return 404, 'Not found'
        except Exception as e:
            return 400, e

    @staticmethod
    def edit_model(model_id, name):
        try:
            edit = Model.query.filter_by(id=model_id).first()
            if edit:
                edit.name = name
                db.session.commit()
                return 200, 'OK'
            else:
                return 404, 'Not found.'
        except Exception as e:
            return 400, e

    @staticmethod
    def get_models():
        all = Model.query.all()
        return all

    @staticmethod
    def add_way(model_id, way_name, start_time):
        try:
            new = Way(model_id=model_id, name=way_name, start_time=start_time)
            db.session.add(new)
            db.session.commit()
            return 200, 'OK'
        except sqlalchemy.exc.IntegrityError:
            return 400, '策略名已存在!'

    @staticmethod
    def delete_way(way_id):
        try:
            delete = Way.query.filter_by(id=way_id).first()
            if delete:
                db.session.delete(delete)
                db.session.commit()
                return 200, 'OK'
            else:
                return 404, 'Not found'
        except Exception as e:
            return 400, e

    @staticmethod
    def edit_way(way_id):
        pass

    @staticmethod
    def get_way(id=None,model_id=None):
        try:
            if id:
                if model_id:
                    way = Way.query.filter_by(id=id,model_id=model_id).all()
                else:
                    way = Way.query.filter_by(id=id).all()
            else:
                if model_id:
                    way = Way.query.filter_by(model_id=model_id).all()
                else:
                    way = Way.query.all()
            if way:
                return way
            else:
                return False
        except Exception as e:
            return False

    @staticmethod
    def add_node():
        pass

    @staticmethod
    def delete_node():
        pass

    @staticmethod
    def edit_node(node_id, price, percentage):
        pass

    @staticmethod
    def query_nodes(way_id=None):
        try:
            if way_id:
                way = Node.query.filter_by(way_id=way_id).order_by(Node.price)
            else:
                way = Node.query.all().order_by(Node.price)
            if way:
                way_all = []
                for w in way:
                    way_all.append(w.turn_json())
                return way_all
            else:
                return False
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_global_settings():
        settings = Global.query.all()
        setting = {}
        for s in settings:
            setting[s.key] = s.value
        return setting

    @staticmethod
    def set_global_settings(settings):
        for s in settings:
            new_setting = Global.query.filter_by(key=s).first()
            if new_setting:
                new_setting.value = settings[s]
                db.session.add_all([new_setting])
            else:
                new_setting = Global(key=s, value=settings[s])
                db.session.add(new_setting)
        db.session.commit()

    @staticmethod
    def datepicker_2_datetime(picker: str):
        """picker = yyyy-mm-dd"""
        time = picker.split('-')
        return datetime.date(year=int(time[0]), month=int(time[1]), day=int(time[2]))
