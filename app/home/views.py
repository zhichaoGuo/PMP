import datetime

from flask import render_template, request, redirect, url_for, Blueprint, current_app, session, jsonify
from flask.views import MethodView
from flask_login import login_user, login_required

from app.forms import LoginForm
from app.models import DataBaseUtils, User

home = Blueprint('home', __name__)


class LoginView(MethodView):
    """
    登录页面
    """

    def get(self):
        current_app.logger.info('-> LoginView')
        # 已登录跳转到index
        if session.get('username') is not None:
            return redirect(url_for('index.index'))
        login_form = LoginForm(request.form)
        return render_template('home/login.html', form=login_form)

    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        current_app.logger.debug('user:%s try to login!' % username)
        # 前端已加防范，后端再防一手
        if username is None:
            current_app.logger.error('login with out username!')
            return jsonify({
                'code': 400,
                'message': '请输入用户名',
                'data': '', })
        if password is None:
            current_app.logger.error('login with out password!')
            return jsonify({
                'code': 400,
                'message': '请输入密码',
                'data': '', })
        test = current_app.ldap.bind_user(username, password)
        # 查询到用户
        if test is not None:
            current_app.logger.info('user:%s is login! from addr:%s' % (username, request.remote_addr))
            # 查询user表中是否有该用户
            user = User.query.filter_by(username=username).first()
            if user:
                user.is_login = True
                user.last_login_ip = request.remote_addr
                user.last_login_time = datetime.datetime.now()
                DataBaseUtils.session_add_all(user)
            else:
                # 不在用户表中，添加进用户表
                current_app.logger.debug('new user:%s wire into DB!' % username)
                DataBaseUtils.record_user(username,request.remote_addr)
                user = User.query.filter_by(username=username).first()
            # 记录登录信息
            login_user(user)
            current_app.logger.info('user:%s is login success!' % username)
            session['username'] = username
            return redirect(url_for('home.home'))
        # 未通过ldap验证
        current_app.logger.info('user:%s is login failed!' % username)
        return jsonify({
            'code': 1,
            'message': '用户名或密码错误',
            'data': '',
        })


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

    @login_required
    def get(self):
        current_app.logger.info('-> RootView')
        return redirect(url_for('home.home'))


class HomeView(MethodView):
    """
    看板页面
    """

    @login_required
    def get(self):
        current_app.logger.info('-> HomeView')
        data = {"all": 150,
                "line": [0, 10, 10, 10, 20, 25, 35, 50, 65, 80, 95, 100]}
        return render_template('home/dashboard.html', data=data)
