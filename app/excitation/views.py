from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from flask.views import MethodView

from app.models import DataBaseUtils

excitation = Blueprint('excitation', __name__)


class ExcitationView(MethodView):
    """
    销售记录页面
    """

    def get(self):
        return render_template('excitation/all_record.html', segment='excitation_all')


class RecordView(MethodView):
    """
    管理销售记录页面
    """

    def get(self):
        data = DataBaseUtils.query_record(seller='yaki.guo')
        return render_template('excitation/record.html', segment='excitation_record',data=data)

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
                    states_code, message = DataBaseUtils.add_record(name=data['name'],time=time,seller='yaki.guo')
            elif data.get('method') == 'edit':
                # ToDo:修改销售记录
                if not data.get('id') or not data.get('name') or not data.get('time'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    time = DataBaseUtils.datepicker_2_datetime(data['time'])
                    states_code, message = DataBaseUtils.edit_record(data['id'],data['name'],time)
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
            states_code, message = 404,'Not found.'
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
        return render_template('excitation/detail.html', segment='excitation_detail')

    def post(self):
        try:
            data = request.get_json()
            if not data.get('method'):
                states_code, message = 404, 'Method not none.'
            elif data.get('method') == 'add':
                # ToDo:添加销售明细
                if not data.get('way_id') or not data.get('price') or not data.get('percentage'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    states_code, message = 200, 'OK'
            elif data.get('method') == 'edit':
                # ToDo:修改销售明细
                if not data.get('way_id') or not data.get('price') or not data.get('percentage'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    states_code, message = 200, 'OK'
            else:
                states_code, message = 400, 'Bad request.'
        except Exception as e:
            states_code, message = 400, str(e)
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })


