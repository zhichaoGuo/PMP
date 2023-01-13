from flask import Blueprint, render_template, request, make_response
from flask.views import MethodView

from app.models import DataBaseUtils

admin = Blueprint('admin', __name__)


class GlobalView(MethodView):
    """
    全局变量管理页面
    """

    def get(self):
        return render_template('admin/global.html', segment='admin_global')


class ModelView(MethodView):
    """
    型号管理页面
    """

    def get(self):
        return render_template('admin/model.html', segment='admin_model')

    def post(self):
        data = request.get_json()
        states_code, message = DataBaseUtils.add_model(data['name'])
        return make_response(message), states_code


class ExcitationView(MethodView):
    """
    激励策略管理页面
    """

    def get(self):
        return render_template('admin/excitation.html', segment='admin_excitation')
