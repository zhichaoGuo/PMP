from flask import Blueprint, render_template
from flask.views import MethodView

admin = Blueprint('admin', __name__)


class GlobalView(MethodView):
    """
    全局变量管理页面
    """
    def get(self):
        return render_template('admin/global.html',segment='admin_global')


class ModelView(MethodView):
    """
    型号管理页面
    """
    def get(self):
        return render_template('admin/model.html',segment='admin_model')


class ExcitationView(MethodView):
    """
    激励策略管理页面
    """
    def get(self):
        return render_template('admin/excitation.html',segment='admin_excitation')