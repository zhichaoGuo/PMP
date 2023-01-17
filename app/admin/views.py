from flask import Blueprint, render_template, request, make_response, redirect, url_for, jsonify
from flask.views import MethodView

from app.models import DataBaseUtils, Model

admin = Blueprint('admin', __name__)


class GlobalView(MethodView):
    """
    全局变量管理页面
    """

    def get(self):
        data = DataBaseUtils.get_global_settings()
        return render_template('admin/global.html', segment='admin_global', data=data)

    def post(self):
        data = request.get_json()
        DataBaseUtils.set_global_settings(data)
        return redirect(url_for('admin.global'))


class ModelView(MethodView):
    """
    型号管理页面
    """

    def get(self):
        data = DataBaseUtils.get_models()
        return render_template('admin/model.html', segment='admin_model', data=data)

    def post(self):
        data = request.get_json()
        states_code, message = DataBaseUtils.add_model(data['model'])
        return jsonify({
            'code': states_code,
            'message': message,
            'data': '',
        })

    def delete(self):
        data = request.get_json()
        states_code, message = DataBaseUtils.delete_model(data['id'])
        return jsonify({
            "code": states_code,
            "message": message,
            'data': '',
        })


class ExcitationView(MethodView):
    """
    激励策略管理页面
    """

    def get(self):

        data = {"models": DataBaseUtils.get_models(), "select_index": 1}

        if request.args.get('model'):
            exci = DataBaseUtils.get_way(request.args['model'])
            data["select_index"] = int(request.args.get('model'))
        else:
            exci = DataBaseUtils.get_way('1')
        if exci:
            data['exci'] = exci
        return render_template('admin/excitation.html', segment='admin_excitation', data=data)

    def post(self):
        data = request.get_json()
        time = DataBaseUtils.datepicker_2_datetime(data['start_time'])
        model = Model.query.filter_by(name=data['model']).first()
        if model:
            data['model_id'] = model.id
            states_code, message = DataBaseUtils.add_way(data['model_id'], data['name'], time)
        else:
            states_code, message = 404, 'Not found.'
        return jsonify({
            "code": states_code,
            "message": message,
            'data': '',
        })

    def delete(self):
        data = request.get_json()
        states_code, message = DataBaseUtils.delete_way(data['id'])
        return jsonify({
            "code": states_code,
            "message": message,
            'data': '',
        })
