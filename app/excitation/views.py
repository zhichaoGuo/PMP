from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from flask.views import MethodView

from app.models import DataBaseUtils

excitation = Blueprint('excitation', __name__)


class ExcitationView(MethodView):
    """
    销售记录页面
    """

    def get(self):
        data = DataBaseUtils.query_all_record('yaki.guo')
        ret = {}
        rec = []
        for d in data:
            if d.Record.id not in rec:
                rec.append(d.Record.id)
                ret[d.Record.id] = {"sale_time": d.Record.sale_time,
                                    "name": d.Record.name,
                                    "seller": d.Record.seller,
                                    "model": [d.Model.name],
                                    "sale_price": [d.Detail.sale_price],
                                    "sale_number": [d.Detail.sale_number],
                                    "sum": [d.Detail.sale_price * d.Detail.sale_number]}
            else:
                ret[d.Record.id]["model"].append(d.Model.name)
                ret[d.Record.id]["sale_price"].append(d.Detail.sale_price)
                ret[d.Record.id]["sale_number"].append(d.Detail.sale_number)
                ret[d.Record.id]["sum"].append(d.Detail.sale_price * d.Detail.sale_number)
        for r in ret:
            ret[r]['all'] = sum(ret[r]['sum'])
        return render_template('excitation/all_record.html', segment='excitation_all', data=ret)


class RecordView(MethodView):
    """
    管理销售记录页面
    """

    def get(self):
        data = DataBaseUtils.query_record(seller='yaki.guo')
        return render_template('excitation/record.html', segment='excitation_record', data=data)

    def post(self):
        try:
            data = request.get_json()
            if not data.get('method'):
                states_code, message = 404, 'Method not none.'
            elif data.get('method') == 'add':
                # ToDo:添加销售记录
                if not data.get('name') or not data.get('time'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    time = DataBaseUtils.datepicker_2_datetime(data['time'])
                    states_code, message = DataBaseUtils.add_record(name=data['name'], time=time, seller='yaki.guo')
            elif data.get('method') == 'edit':
                # ToDo:修改销售记录
                if not data.get('id') or not data.get('name') or not data.get('time'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    time = DataBaseUtils.datepicker_2_datetime(data['time'])
                    states_code, message = DataBaseUtils.edit_record(data['id'], data['name'], time)
            else:
                states_code, message = 400, 'Bad request.'
        except Exception as e:
            states_code, message = 400, str(e)
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })

    def delete(self):
        data = request.get_json()
        if data.get('id'):
            states_code, message = DataBaseUtils.delete_record(data['id'])
        else:
            states_code, message = 404, 'Not found.'
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })


class DetailView(MethodView):
    """
    管理销售明细页面
    """

    def get(self):
        record = DataBaseUtils.query_record(seller='yaki.guo')
        models = DataBaseUtils.query_models()
        data = {"record": record, "select_index": record[0].id, "models": models, "select_index2": models[0].id}
        if request.args.get('record_id'):
            details = DataBaseUtils.query_detail(record_id=request.args['record_id'])
            data["select_index"] = int(request.args.get('record_id'))
        else:
            details = DataBaseUtils.query_detail(record_id=record[0].id)  # 默认展示第一个option的策略
        if details:
            data['details'] = details

        return render_template('excitation/detail.html', segment='excitation_detail', data=data)

    def post(self):
        try:
            data = request.get_json()
            if not data.get('method'):
                states_code, message = 404, 'Method not none.'
            elif data.get('method') == 'add':
                if not data.get('record_id') or not data.get('model_id') or not data.get('price') or not data.get(
                        'number'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    states_code, message = DataBaseUtils.add_detail(record_id=data['record_id'],
                                                                    model_id=data['model_id'], price=data['price'],
                                                                    number=data['number'])
            elif data.get('method') == 'edit':
                # ToDo:修改销售明细
                if not data.get('id') or not data.get('price') or not data.get('number'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    states_code, message = DataBaseUtils.edit_detail(detail_id=data['id'], price=data['price'],
                                                                     number=data['number'])
            else:
                states_code, message = 400, 'Bad request.'
        except Exception as e:
            states_code, message = 400, str(e)
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })

    def delete(self):
        data = request.get_json()
        if data.get('id'):
            states_code, message = DataBaseUtils.delete_detail(data['id'])
        else:
            states_code, message = 404, 'Not found.'
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })
