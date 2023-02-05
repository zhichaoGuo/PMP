from flask import render_template, request, redirect, url_for, Blueprint, jsonify, current_app, session
from flask.views import MethodView
from flask_login import login_required

from app.models import DataBaseUtils

excitation = Blueprint('excitation', __name__)


class ExcitationView(MethodView):
    """
    销售记录页面
    """

    @login_required
    def get(self):
        current_app.logger.info('User: %s -> ExcitationView' % session.get("username"))
        admin = {"all_user": DataBaseUtils.query_all_user(), "select_index": 0}
        if request.args.get('admin_user_name'):
            record_user = request.args.get('admin_user_name')
        else:
            record_user = session.get("username")
        if request.args.get('index'):
            admin['select_index'] = int(request.args.get('index'))
        else:
            admin['select_index'] = int(session.get("_user_id"))
        global_settings = DataBaseUtils.get_global_settings()
        data = DataBaseUtils.query_all_record(record_user, start_time=global_settings['start_time'],
                                              end_time=global_settings['end_time'])
        setting = {"settings": global_settings, "number_limit": 0}
        setting["settings"]["start_number"] = int(setting["settings"]["start_number"])
        for d in data:
            setting['number_limit'] += data[d]['all_number']

        return render_template('excitation/all_record.html', segment='excitation_all', data=data, setting=setting,
                               admin=admin)



class RecordView(MethodView):
    """
    管理销售记录页面
    """

    @login_required
    def get(self):
        current_app.logger.info('User: %s -> RecordView' % session.get("username"))
        data = DataBaseUtils.query_record(seller=session.get("username"))
        return render_template('excitation/record.html', segment='excitation_record', data=data)

    @login_required
    def post(self):
        try:
            data = request.get_json()
            if not data.get('method'):
                states_code, message = 404, 'Method not none.'
            elif data.get('method') == 'add':
                if not data.get('name') or not data.get('time'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    time = DataBaseUtils.datepicker_2_datetime(data['time'])
                    states_code, message = DataBaseUtils.add_record(name=data['name'], time=time,
                                                                    seller=session.get("username"))
                current_app.logger.info('User: %s -> add record : %s -> ret : %s,%s' % (
                    session.get("username"), data, states_code, message))
            elif data.get('method') == 'edit':
                if not data.get('id') or not data.get('name') or not data.get('time'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    time = DataBaseUtils.datepicker_2_datetime(data['time'])
                    states_code, message = DataBaseUtils.edit_record(data['id'], data['name'], time)
                current_app.logger.info('User: %s -> edit record : %s -> ret : %s,%s' % (
                    session.get("username"), data, states_code, message))
            else:
                states_code, message = 400, 'Bad request.'
        except Exception as e:
            states_code, message = 400, str(e)
            current_app.logger.error('User: %s -> post record : %s -> ret : %s,%s' % (
                session.get("username"), data, states_code, message))
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })

    @login_required
    def delete(self):
        data = request.get_json()
        if data.get('id'):
            states_code, message = DataBaseUtils.delete_record(data['id'])
        else:
            states_code, message = 404, 'Not found.'
        current_app.logger.warn('User: %s -> delete record : %s -> ret : %s,%s' % (
            session.get("username"), data, states_code, message))
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })


class DetailView(MethodView):
    """
    管理销售明细页面
    """

    @login_required
    def get(self):
        current_app.logger.info('User: %s -> DetailView' % session.get("username"))
        record = DataBaseUtils.query_record(seller=session.get("username"))
        models = DataBaseUtils.query_models()
        select_index = record[0].id if record else 0
        select_index2 = models[0].id if models else 0
        data = {"record": record, "select_index": select_index, "models": models, "select_index2": select_index2}
        if request.args.get('record_id'):
            details = DataBaseUtils.query_detail(record_id=request.args['record_id'])
            data["select_index"] = int(request.args.get('record_id'))
        else:
            details = DataBaseUtils.query_detail(record_id=select_index)  # 默认展示第一个option的策略
        if details:
            data['details'] = details

        return render_template('excitation/detail.html', segment='excitation_detail', data=data)

    @login_required
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
                current_app.logger.info('User: %s -> add detail : %s -> ret : %s,%s' % (
                    session.get("username"), data, states_code, message))
            elif data.get('method') == 'edit':
                if not data.get('id') or not data.get('price') or not data.get('number'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    states_code, message = DataBaseUtils.edit_detail(detail_id=data['id'], price=data['price'],
                                                                     number=data['number'])
                current_app.logger.info('User: %s -> edit detail : %s -> ret : %s,%s' % (
                    session.get("username"), data, states_code, message))
            else:
                states_code, message = 400, 'Bad request.'
        except Exception as e:
            states_code, message = 400, str(e)
            current_app.logger.error('User: %s -> post detail : %s -> ret : %s,%s' % (
                session.get("username"), data, states_code, message))
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })

    @login_required
    def delete(self):
        data = request.get_json()
        if data.get('id'):
            states_code, message = DataBaseUtils.delete_detail(detail_id=data['id'])
        else:
            states_code, message = 404, 'Not found.'
        current_app.logger.warn('User: %s -> delete detail : %s -> ret : %s,%s' % (
            session.get("username"), data, states_code, message))
        return jsonify({
            "code": states_code,
            "message": message,
            "data": '',
        })
