from flask import render_template, request, redirect, url_for, Blueprint
from flask.views import MethodView

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
        return render_template('excitation/record.html', segment='excitation_record')


class DetailView(MethodView):
    """
    管理销售明细页面
    """

    def get(self):
        return render_template('excitation/detail.html', segment='excitation_detail')


