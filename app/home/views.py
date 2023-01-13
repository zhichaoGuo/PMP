from flask import render_template, request, redirect, url_for, Blueprint
from flask.views import MethodView

from app.forms import LoginForm

home = Blueprint('home', __name__)


class LoginView(MethodView):
    """
    登录页面
    """
    def get(self):
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
        return redirect(url_for('home.login'))


class RootView(MethodView):
    """
    根页面跳转至看板页面
    """
    def get(self):
        return redirect(url_for('home.home'))


class HomeView(MethodView):
    """
    看板页面
    """
    def get(self):
        return render_template('home/dashboard.html')

