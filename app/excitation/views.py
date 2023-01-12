from flask import render_template, request, redirect, url_for, Blueprint
from flask.views import MethodView

excitation = Blueprint('excitation', __name__)


class ExcitationView(MethodView):
    """
    激励页面
    """
    def get(self):
        return render_template('excitation/tables.html',segment='excitation_tables')


