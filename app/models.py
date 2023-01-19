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
    percentage = db.Column(db.Float, nullable=False)

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
    seller = db.Column(db.String(64), nullable=False)
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
                DataBaseUtils.delete_way(model_id=model_id)
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
    def query_models():
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
    def delete_way(model_id=None, way_id=None):
        try:
            if model_id:
                delete_way = Way.query.filter_by(model_id=model_id).all()
                for d in delete_way:
                    DataBaseUtils.delete_way(way_id=d.id)
            if way_id:
                delete = Way.query.filter_by(id=way_id).first()
                if delete:
                    DataBaseUtils.delete_node(way_id=way_id)
                    db.session.delete(delete)
                    db.session.commit()
                    return 200, 'OK'
                else:
                    return 404, 'Not found'
            return 400, 'Bad request.'
        except Exception as e:
            return 400, e

    @staticmethod
    def edit_way(way_id, name, start_time):
        try:
            Way.query.filter_by(id=way_id).update({"name": name, "start_time": start_time})
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def query_way(id=None, model_id=None):
        try:
            if id:
                if model_id:
                    way = Way.query.filter_by(id=id, model_id=model_id).all()
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
    def add_node(way_id, price, percentage):
        try:
            old = Node.query.filter_by(way_id=way_id, price=price).first()
            if old:
                return 400, '策略中已包含相同底价的节点！'
            down = Node.query.filter_by(way_id=way_id).filter(Node.price.__lt__(price)).order_by(-Node.price).first()
            _down = down.percentage if down else 0
            up = Node.query.filter_by(way_id=way_id).filter(Node.price.__gt__(price)).order_by(Node.price).first()
            _up = up.percentage if up else float(100)
            if float(percentage) <= _down or float(percentage) >= _up:
                return 400, '底价 %s 的激励百分比应该在[%s-%s]区间内！' % (price, _down, _up)
            new = Node(way_id=way_id, price=price, percentage=percentage)
            db.session.add(new)
            db.session.commit()
            return 200, 'OK'

        except sqlalchemy.exc.IntegrityError:
            return 400, '策略名已存在!'

    @staticmethod
    def delete_node(way_id=None, node_id=None):
        try:
            if way_id:
                dele = Node.query.filter_by(way_id=way_id).delete()
                db.session.commit()
                return 200, 'OK'
            if node_id:
                dele = Node.query.filter_by(id=node_id).delete()
                db.session.commit()
                return 200, 'OK'
            return 400, 'Bad request.'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def edit_node(node_id, price, percentage):
        try:
            way_id = Node.query.filter_by(id=node_id).first().way_id
            old = Node.query.filter_by(way_id=way_id, price=price).first()
            if old:  # 存在想要修改到的价格的节点
                if old.id != int(node_id):
                    return 400, '存在价格为 %s 的节点，ID为%s' % (price, old.id)
            down = Node.query.filter_by(way_id=way_id).filter(Node.id != node_id).filter(
                Node.price.__lt__(price)).order_by(-Node.price).first()
            _down = down.percentage if down else 0
            up = Node.query.filter_by(way_id=way_id).filter(Node.id != node_id).filter(
                Node.price.__gt__(price)).order_by(Node.price).first()
            _up = up.percentage if up else float(100)
            if float(percentage) <= _down or float(percentage) >= _up:
                return 400, '底价 %s 的激励百分比应该在[%s-%s]区间内！' % (price, _down, _up)
            Node.query.filter_by(id=node_id).update({"price": price, "percentage": percentage})
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

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
    def add_record(name, time, seller):
        try:
            new = Record(name=name, sale_time=time, seller=seller)
            db.session.add(new)
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def delete_record(id):  # ToDo:删除名下的明细
        try:
            dele = Record.query.filter_by(id=id).delete()
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def edit_record(id, name, time):
        try:
            edit = Record.query.filter_by(id=id).update({"name": name, "sale_time": time})
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def query_record(seller):
        try:
            data = Record.query.filter_by(seller=seller).all()
            return data
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def add_detail(record_id, model_id, price, time, number):  # ToDo:同一record_id中的model_id不应该相同
        try:
            new = Detail(record_id=record_id, model_id=model_id, sale_price=price, sale_time=time, sale_number=number)
            db.session.add(new)
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def delete_detail():  # ToDo
        pass

    @staticmethod
    def edit_detail():  # ToDo
        pass

    @staticmethod
    def query_detail(record_id):  # ToDo
        pass

    @staticmethod
    def datepicker_2_datetime(picker: str):
        """picker = yyyy-mm-dd"""
        time = picker.split('-')
        return datetime.date(year=int(time[0]), month=int(time[1]), day=int(time[2]))
