from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from flask.views import MethodView

from app.models import DataBaseUtils

excitation = Blueprint('excitation', __name__)


class ExcitationView(MethodView):
    """
    销售记录页面
    """

    def get(self):
        global_settings = DataBaseUtils.get_global_settings()
        data = DataBaseUtils.query_all_record('yaki.guo', start_time=global_settings['start_time'])
        setting = {"settings": global_settings, "number_limit": 0}
        setting["settings"]["start_number"] = int(setting["settings"]["start_number"])
        for d in data:
            setting['number_limit'] += data[d]['all_number']


        return render_template('excitation/all_record.html', segment='excitation_all', data=data, setting=setting)

    def post(self):
        DataBaseUtils.query_all_record_in_limit('yaki.guo', '2023-1-3')
        return '200'


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
            states_code, message = DataBaseUtils.delete_detail(detail_id=data['id'])
        else:
            states_code, message = 404, 'Not found.'
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })
