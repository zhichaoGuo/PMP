import datetime

import sqlalchemy
from sqlalchemy import event
from werkzeug.security import generate_password_hash

import app.config
from app import db


class User(db.Model):  # 用户表
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    username = db.Column(db.String(63), unique=True)
    last_login_ip = db.Column(db.String(15))
    last_login_time = db.Column(db.DateTime(), default=datetime.datetime.now())
    status = db.Column(db.Boolean(), default=False)
    is_login = db.Column(db.Boolean(), default=False)
    is_active = True
    is_authenticated = True

    def __repr__(self):
        return self.username

    def get_id(self):
        return self.id

    def is_admin(self):
        if self.username in app.config.Config.ADMIN_GROUP:
            return True
        else:
            return False


class Model(db.Model):  # 型号表
    __tablename__ = 'Model'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return str(self.name)

    def query_percentage(self, price, sale_time):
        if type(sale_time) is str:
            time = DataBaseUtils.datepicker_2_datetime(sale_time)
        else:
            time = sale_time
        data = Way.query.filter_by(model_id=self.id).filter(Way.start_time.__le__(time)) \
            .order_by(Way.start_time.desc()).first()
        if data:
            return data.query_percentage(price)
        else:
            return 0

    def query_floor_price(self, sale_time):
        if type(sale_time) is str:
            time = DataBaseUtils.datepicker_2_datetime(sale_time)
        else:
            time = sale_time
        data = Way.query.filter_by(model_id=self.id).filter(Way.start_time.__le__(time)) \
            .order_by(Way.start_time.desc()).first()
        if data:
            return data.query_floor_price()
        else:
            return 0

    def query_lower_all_nodes(self, price, sale_time):
        """
        查询此型号下sale time对应的策略way中价格低于price的所有节点，返回价格由大到小排列的node的列表
        :param price: float
        :param sale_time: str or datatime
        :return: list
        """
        if type(sale_time) is str:
            time = DataBaseUtils.datepicker_2_datetime(sale_time)
        else:
            time = sale_time
        cur_way = Way.query.filter_by(model_id=self.id).filter(Way.start_time.__le__(time)) \
            .order_by(Way.start_time.desc()).first()
        if cur_way:
            return cur_way.query_lower_all_nodes(price)
        else:
            return []


class Way(db.Model):  # 激励策略表
    __tablename__ = 'Way'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(64), unique=True)
    start_time = db.Column(db.Date, default=datetime.date.today())
    status = db.Column(db.Boolean(), default=False)

    def query_percentage(self, price):
        data = Node.query.filter_by(way_id=self.id).filter(Node.price.__le__(price)).order_by(-Node.price).first()
        if data:
            percentage = data.percentage
        else:
            percentage = 0
        return percentage

    def query_floor_price(self):
        data = Node.query.filter_by(way_id=self.id).order_by(Node.price).first()
        if data:
            floor_price = data.price
        else:
            floor_price = 0
        return floor_price

    def query_lower_all_nodes(self, price):
        """
        查询本条策略中价格低于price的所有节点，返回价格由大到小排列的node的列表
        :param price:float
        :return: list
        """
        data = Node.query.filter_by(way_id=self.id).filter(Node.price.__lt__(price)).order_by(-Node.price).all()
        return data


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
    sale_time = db.Column(db.Date, default=datetime.date.today())


class Detail(db.Model):  # 销售明细表
    __tablename__ = 'Detail'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_id = db.Column(db.Integer, nullable=False)
    model_id = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    sale_number = db.Column(db.Integer, nullable=False)


class Global(db.Model):  # 全局配置表
    __tablename__ = 'Global'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(64), nullable=False)


@event.listens_for(Global.__table__, 'after_create')
def init_global(*args, **kwargs):
    settings = {"start_time": "2010-1-1",
                "end_time": "2050-1-1"}
    for s in settings:
        new_setting = Global(key=s, value=settings[s])
        db.session.add(new_setting)
    db.session.commit()


class Number(db.Model):  # 数量激励表
    __tablename__ = 'Number'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    ratio = db.Column(db.Float, nullable=False)

    @staticmethod
    def query_all():
        data = Number.query.all()
        return data

    @staticmethod
    def query_ratio(number):
        query = Number.query.filter(Number.number.__le__(number)).order_by(-Number.number).first()
        if query:
            ret = query.ratio
        else:
            ret = 0
        return ret

    @staticmethod
    def add(number, ratio):
        try:
            if Number.query.filter_by(number=number).first():
                return 400, '数量激励节点已存在!'
            down = Number.query.filter(Number.number.__lt__(number)).order_by(-Number.number).first()
            _down = down.ratio if down else 0
            up = Number.query.filter(Number.number.__gt__(number)).order_by(Number.number).first()
            _up = up.ratio if up else float(1)
            if _up == 1:
                if float(ratio) <= _down or float(ratio) > _up:
                    return 400, '数量激励节点 %s 的激励系数应该在[%s-%s]区间内！' % (number, _down, _up)
            else:
                if float(ratio) <= _down or float(ratio) >= _up:
                    return 400, '数量激励节点 %s 的激励系数应该在[%s-%s]区间内！' % (number, _down, _up)
            new = Number(number=number, ratio=ratio)
            db.session.add(new)
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, e

    @staticmethod
    def delete(number_id):
        try:
            delete = Number.query.filter_by(id=number_id).first()
            if delete:
                db.session.delete(delete)
                db.session.commit()
                return 200, 'OK'
            else:
                return 404, 'Not found'
        except Exception as e:
            return 400, e

    @staticmethod
    def edit(number_id, number, ratio):
        try:
            check = Number.query.filter_by(number=number).first()
            if check:
                if check.id != int(number_id):
                    print(type(check.id))
                    print(type(number_id))
                    return 400, '数量激励节点 %s 已存在!' % number
            down = Number.query.filter(Number.number.__lt__(number)).order_by(-Number.number).first()
            _down = down.ratio if down else 0
            up = Number.query.filter(Number.number.__gt__(number)).order_by(Number.number).first()
            _up = up.ratio if up else float(1)
            if _up == 1:
                if float(ratio) <= _down or float(ratio) > _up:
                    return 400, '数量激励节点 %s 的激励系数应该在[%s-%s]区间内！' % (ratio, _down, _up)
            else:
                if float(ratio) <= _down or float(ratio) >= _up:
                    return 400, '数量激励节点 %s 的激励系数应该在[%s-%s]区间内！' % (ratio, _down, _up)

            edit = Number.query.filter_by(id=number_id).first()
            edit.number = number
            edit.ratio = ratio
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, e


@event.listens_for(Number.__table__, 'after_create')
def init_global(*args, **kwargs):
    init_number = Number(number=3000, ratio=0.2)
    db.session.add(init_number)
    db.session.commit()


class DataBaseUtils:
    @staticmethod
    def record_user(user_name, remote_ip):
        new_user = User(username=user_name, last_login_ip=remote_ip, last_login_time=datetime.datetime.now(),
                        is_login=True)
        db.session.add(new_user)
        db.session.commit()

    @staticmethod
    def query_all_user():
        data = User.query.all()
        return data

    @staticmethod
    def session_add_all(user):
        db.session.add_all([user])
        db.session.commit()

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
    def delete_model(model_id):
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
    def query_model(model_id):
        model = Model.query.filter_by(id=model_id).first()
        if model:
            return model
        else:
            return False

    @staticmethod
    def query_models():
        all = Model.query.all()
        return all

    @staticmethod
    def add_way(model_id, way_name, start_time):
        try:
            data = Way.query.filter_by(model_id=model_id, start_time=start_time).first()
            if data:
                return 400, '同一型号下激励策略的起始时间不能相同'
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
                way = Node.query.filter_by(way_id=way_id).order_by(Node.price).all()
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
        return 200, 'OK'

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
    def delete_record(id):
        try:
            dele = Record.query.filter_by(id=id).delete()
            DataBaseUtils.delete_detail(record_id=id)
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
            data = Record.query.filter_by(seller=seller).order_by(Record.sale_time.desc()).all()  # 按时间倒序排列
            return data
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def add_detail(record_id, model_id, price, number):  # ToDo:同一record_id中的model_id不应该相同
        try:
            new = Detail(record_id=record_id, model_id=model_id, sale_price=price, sale_number=number)
            db.session.add(new)
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def delete_detail(detail_id=None, record_id=None):
        try:
            if not detail_id and not record_id:
                return 404, 'Not found.'
            elif detail_id:
                delete = Detail.query.filter_by(id=detail_id).delete()
            elif record_id:
                delete = Detail.query.filter_by(record_id=record_id).delete()
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def edit_detail(detail_id, price, number):
        try:
            edit = Detail.query.filter_by(id=detail_id).update({"sale_price": price, "sale_number": number})
            db.session.commit()
            return 200, 'OK'
        except Exception as e:
            return 400, str(e)

    @staticmethod
    def query_detail(record_id):
        try:
            data = Detail.query.filter_by(record_id=record_id).all()
            for detail in data:
                detail.model_id = Model.query.filter_by(id=detail.model_id).first().name
            return data
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def datepicker_2_datetime(picker: str):
        """picker = yyyy-mm-dd"""
        time = picker.split('-')
        return datetime.date(year=int(time[0]), month=int(time[1]), day=int(time[2]))

    @staticmethod
    def query_all_record(seller, start_time='2000-1-1', end_time=''):  # 此处返回的激励数值未乘以数量激励系数，数量激励系数在前端计算
        start_time_format = DataBaseUtils.datepicker_2_datetime(start_time)
        if not end_time:
            end_time_format = datetime.date.today()
        else:
            end_time_format = DataBaseUtils.datepicker_2_datetime(end_time)
        data = db.session.query(Detail, Record, Model) \
            .join(Record, Detail.record_id == Record.id) \
            .join(Model, Detail.model_id == Model.id) \
            .filter(Record.seller == seller) \
            .filter(Record.sale_time.__ge__(start_time_format)) \
            .filter(Record.sale_time.__le__(end_time_format)) \
            .order_by(Record.sale_time.desc()).all()
        ret = {}
        rec = []
        for d in data:
            excitation = round(DataBaseUtils.query_excitation(model_id=d.Model.id, price=d.Detail.sale_price,
                                                              sale_time=d.Record.sale_time) * d.Detail.sale_number, 1)
            if d.Record.id not in rec:  # 此条明细属于新的记录
                rec.append(d.Record.id)
                ret[d.Record.id] = {"sale_time": d.Record.sale_time,
                                    "name": d.Record.name,
                                    "seller": d.Record.seller,
                                    "model": [d.Model.name],
                                    "sale_price": [d.Detail.sale_price],
                                    "sale_number": [d.Detail.sale_number],
                                    "sum": [d.Detail.sale_price * d.Detail.sale_number],
                                    "excitation": [excitation]}
            else:  # 此条明细已存在记录
                ret[d.Record.id]["model"].append(d.Model.name)
                ret[d.Record.id]["sale_price"].append(d.Detail.sale_price)
                ret[d.Record.id]["sale_number"].append(d.Detail.sale_number)
                ret[d.Record.id]["sum"].append(d.Detail.sale_price * d.Detail.sale_number)
                ret[d.Record.id]["excitation"].append(excitation)
        for r in ret:
            ret[r]['all'] = sum(ret[r]['sum'])
            ret[r]['all_excitation'] = sum(ret[r]['excitation'])
            ret[r]['all_number'] = sum(ret[r]['sale_number'])
        return ret

    @staticmethod
    def query_all_record_in_limit(seller, start_time):
        time = DataBaseUtils.datepicker_2_datetime(start_time)
        return Record.query.filter_by(seller=seller).filter(Record.sale_time.__ge__(time)).order_by(
            Record.sale_time).all()

    @staticmethod
    def query_excitation(model_id, price, sale_time):
        """
        计算特定型号下sale time时执行的策略中价格为price时的激励奖金（此为百分比，未乘数量）
        :param model_id:
        :param price:
        :param sale_time:
        :return:
        """
        all_lower_node = Model(id=model_id).query_lower_all_nodes(price=price, sale_time=sale_time)
        lower_price = 0
        higher_price = price
        pre_exci = 0
        if all_lower_node is []:
            return 0
        for node in all_lower_node:
            lower_price = node.price
            pre_exci += (higher_price - lower_price) * node.percentage
            print('[%s-%s]%s=>%s' % (lower_price, higher_price, price, pre_exci))
            higher_price = node.price
        return round(pre_exci / 100, 1)

    @staticmethod
    def query_number(number=None):
        if number:
            num = Number.query.filter(Number.number.__le__(number)).order_by(-Number.number).first().number
        else:
            num = Number.query.order_by(Number.number).first().number
        return num
