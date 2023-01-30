from flask import render_template, request, redirect, url_for, Blueprint, current_app
from flask.views import MethodView

from app.forms import LoginForm

home = Blueprint('home', __name__)


class LoginView(MethodView):
    """
    登录页面
    """

    def get(self):
        current_app.logger.info('-> LoginView')
        login_form = LoginForm(request.form)

        return render_template('home/login.html', form=login_form)

    def post(self):
        data = request.get_json()
        return 1


class LogoutView(MethodView):
    """
    登出页面
    """

    def get(self):
        current_app.logger.info('-> LogoutView')
        return redirect(url_for('home.login'))


class RootView(MethodView):
    """
    根页面跳转至看板页面
    """

    def get(self):
        current_app.logger.info('-> RootView')
        return redirect(url_for('home.home'))


class HomeView(MethodView):
    """
    看板页面
    """

    def get(self):
        current_app.logger.info('-> HomeView')
        data = {"all": 150,
                "line": [0, 10, 10, 10, 20, 25, 35, 50, 65, 80, 95, 100]}
        return render_template('home/dashboard.html', data=data)
