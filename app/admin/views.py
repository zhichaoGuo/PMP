from flask import Blueprint, render_template, request, make_response, redirect, url_for, jsonify, current_app, session
from flask.views import MethodView
from flask_login import login_required

from app.models import DataBaseUtils, Model, Number

admin = Blueprint('admin', __name__)


class GlobalView(MethodView):
    """
    全局变量管理页面
    """

    @login_required
    def get(self):
        current_app.logger.info('User: %s -> GlobalView' % session.get("username"))
        data = DataBaseUtils.get_global_settings()
        data['number'] = Number.query_all()
        return render_template('admin/global.html', segment='admin_global', data=data)

    @login_required
    def post(self):
        data = request.get_json()
        if DataBaseUtils.datepicker_2_datetime(data.get('start_time')) >= DataBaseUtils.datepicker_2_datetime(
                data.get('end_time')):
            states_code, message = 400, '激励计算开始时间应晚于结束时间！'
        else:
            states_code, message = DataBaseUtils.set_global_settings(data)
        current_app.logger.info(
            'User: %s -> set global settings : %s -> ret : %s' % (session.get("username"), data, states_code))
        return jsonify({
            'code': states_code,
            'message': message,
            'data': '',
        })


class NumberView(MethodView):
    def post(self):
        data = request.get_json()
        if data.get('method') == 'add':
            if not data.get('number') or not data.get('ratio'):
                states_code, message = 400, '参数不能为空!'
            else:
                states_code, message = Number.add(number=data['number'], ratio=data['ratio'])
                current_app.logger.info('User: %s -> add number : %s -> ret : %s,%s' % (
                    session.get("username"), data, states_code, message))
        elif data.get('method') == 'delete':
            if not data.get('id'):
                states_code, message = 400, '编辑的number id不能为空!'
            else:
                states_code, message = Number.delete(number_id=data['id'])
                current_app.logger.warn('User: %s -> delete number : %s -> ret : %s,%s' % (
                    session.get("username"), data, states_code, message))
        elif data.get('method') == 'edit':
            if not data.get('id'):
                states_code, message = 400, '编辑的number id不能为空!'
            else:
                if not data.get('number') or not data.get('ratio'):
                    states_code, message = 400, '参数不能为空!'
                else:
                    states_code, message = Number.edit(number_id=data['id'], number=data['number'], ratio=data['ratio'])
                    current_app.logger.info('User: %s -> edit number : %s -> ret : %s,%s' % (
                        session.get("username"), data, states_code, message))
        else:
            states_code, message = 400, 'method 字段无法识别.'
            current_app.logger.warn('User: %s -> post number :%s -> ret:%s' % (session.get("username"), data, message))
        return jsonify({
            'code': states_code,
            'message': message,
            'data': '',
        })


class ModelView(MethodView):
    """
    型号管理页面
    """

    @login_required
    def get(self):
        current_app.logger.info('User: %s -> ModelView' % session.get("username"))
        data = DataBaseUtils.query_models()
        return render_template('admin/model.html', segment='admin_model', data=data)

    @login_required
    def post(self):
        data = request.get_json()
        if not data.get('method') or not data.get('model'):
            states_code, message = 400, '参数不能为空!'
        elif data['method'] == 'add':
            states_code, message = DataBaseUtils.add_model(data['model'])
            current_app.logger.info(
                'User: %s -> add model : %s -> ret : %s,%s' % (session.get("username"), data, states_code, message))
        elif data['method'] == 'edit':
            if not data.get('model_id'):
                states_code, message = 400, '参数不能为空!'
                current_app.logger.warn(
                    'User: %s -> edit model :%s -> ret:%s' % (session.get("username"), data, message))
            else:
                states_code, message = DataBaseUtils.edit_model(data['model_id'], data['model'])
                current_app.logger.info('User: %s -> edit model : %s -> ret : %s,%s' % (
                    session.get("username"), data, states_code, message))
        else:
            states_code, message = 400, 'method 字段无法识别.'
            current_app.logger.warn('User: %s -> post model :%s -> ret:%s' % (session.get("username"), data, message))
        return jsonify({
            'code': states_code,
            'message': message,
            'data': '',
        })

    @login_required
    def delete(self):
        data = request.get_json()
        states_code, message = DataBaseUtils.delete_model(data['id'])
        current_app.logger.warn(
            'User: %s -> delete model : %s -> ret : %s,%s' % (session.get("username"), data, states_code, message))
        return jsonify({
            "code": states_code,
            "message": message,
            'data': '',
        })


class ExcitationView(MethodView):
    """
    激励策略管理页面
    """

    @login_required
    def get(self):
        current_app.logger.info('User: %s -> ExcitationView' % session.get("username"))
        models = DataBaseUtils.query_models()
        select_index = models[0].id if models else 0
        data = {"models": models, "select_index": select_index}

        if request.args.get('model'):
            exci = DataBaseUtils.query_way(model_id=request.args['model'])
            data["select_index"] = int(request.args.get('model'))
        else:
            exci = DataBaseUtils.query_way(model_id=select_index)  # 默认展示第一个option的策略
        if exci:
            data['exci'] = exci
        return render_template('admin/excitation.html', segment='admin_excitation', data=data)

    @login_required
    def post(self):
        data = request.get_json()
        return_data = ''
        if not data.get('method'):
            states_code, message = 404, 'Method not none.'
        elif data.get('method') == 'add':
            if not data.get('start_time') or not data.get('name') or not data.get('model'):
                states_code, message = 400, '参数不能为空!'
                current_app.logger.warn(
                    'User: %s -> add excitation : %s -> ret : %s' % (session.get("username"), data, message))
            else:
                time = DataBaseUtils.datepicker_2_datetime(data['start_time'])
                model = Model.query.filter_by(name=data['model']).first()
                if model:
                    data['model_id'] = model.id
                    states_code, message = DataBaseUtils.add_way(data['model_id'], data['name'], time)
                else:
                    states_code, message = 404, 'Not found.'
                    current_app.logger.warn(
                        'User: %s -> add excitation : %s -> ret : %s' % (session.get("username"), data, message))
        elif data.get('method') == 'query':
            return_data = DataBaseUtils.query_nodes(data.get('id'))
            if return_data:
                states_code, message = 200, 'OK'
            else:
                states_code, message = 404, 'Not found.'
                current_app.logger.warn(
                    'User: %s -> query excitation : %s -> ret : %s' % (session.get("username"), data, message))
        elif data.get('method') == 'edit':
            if not data.get('start_time') or not data.get('name') or not data.get('id'):
                states_code, message = 400, '参数不能为空!'
                current_app.logger.warn(
                    'User: %s -> edit excitation : %s -> ret : %s' % (session.get("username"), data, message))
            else:
                time = DataBaseUtils.datepicker_2_datetime(data['start_time'])
                states_code, message = DataBaseUtils.edit_way(data.get('id'), data.get('name'), time)
                current_app.logger.info('User: %s -> edit excitation : %s -> ret : %s,%s' % (
                    session.get("username"), data, states_code, message))
        else:
            states_code, message = 400, 'Bad request.'
        return jsonify({
            "code": states_code,
            "message": message,
            'data': return_data,
        })

    @login_required
    def delete(self):
        data = request.get_json()
        states_code, message = DataBaseUtils.delete_way(way_id=data['id'])
        current_app.logger.warn('User: %s -> delete excitation : %s -> ret : %s,%s' % (
            session.get("username"), data, states_code, message))
        return jsonify({
            "code": states_code,
            "message": message,
            'data': '',
        })


class NodeView(MethodView):
    """
    节点管理页面
    """

    @login_required
    def get(self):
        current_app.logger.info('User: %s -> NodeView' % session.get("username"))
        data = {"models": DataBaseUtils.query_models(), "select_index": 1}
        if request.args.get('exci'):  # 指定策略
            model_index = DataBaseUtils.query_way(id=request.args.get('exci'))[0].model_id
            node = DataBaseUtils.query_nodes(request.args.get('exci'))
            data['exci'] = DataBaseUtils.query_way(model_id=model_index)
            data["select_index"] = model_index
            data["select_index2"] = int(request.args.get('exci'))
        else:
            if request.args.get('model'):  # 指定型号
                if not DataBaseUtils.query_way(model_id=request.args['model']):  # 型号未创建策略
                    data['exci'] = [{"id": 0, "name": "请先创建策略！"}]
                    data["select_index2"] = 0
                    node = []
                else:
                    exci_index = DataBaseUtils.query_way(model_id=request.args['model'])[0].id
                    node = DataBaseUtils.query_nodes(exci_index)
                    data['exci'] = DataBaseUtils.query_way(model_id=request.args['model'])
                    data["select_index2"] = int(exci_index)
                data["select_index"] = int(request.args.get('model'))
            else:  # 未指定型号
                exci_index = DataBaseUtils.query_way(model_id=1)[0].id if DataBaseUtils.query_way(model_id=1) else 0
                node = DataBaseUtils.query_nodes(exci_index)
                data['exci'] = DataBaseUtils.query_way(model_id=1) if DataBaseUtils.query_way(model_id=1) else []
                data["select_index2"] = int(exci_index)
        if node:
            data["node"] = node
        return render_template('admin/node.html', segment='admin_node', data=data)

    @login_required
    def post(self):
        data = request.get_json()
        return_data = ""
        if not data.get('method'):
            states_code, message = 404, 'Method not none.'
        elif data.get('method') == 'add':
            if not data.get('way_id') or not data.get('price') or not data.get('percentage'):
                states_code, message = 400, '参数不能为空!'
            else:
                states_code, message = DataBaseUtils.add_node(data.get('way_id'), data.get('price'),
                                                              data.get('percentage'))
            current_app.logger.info('User: %s -> add node : %s -> ret : %s,%s' % (
                session.get("username"), data, states_code, message))
        elif data.get('method') == 'edit':
            states_code, message = DataBaseUtils.edit_node(data.get('node_id'), data.get('price'),
                                                           data.get('percentage'))
            current_app.logger.info('User: %s -> edit node : %s -> ret : %s,%s' % (
                session.get("username"), data, states_code, message))
        else:
            states_code, message = 400, 'Bad request.'
        return jsonify({
            "code": states_code,
            "message": message,
            "data": return_data,
        })

    @login_required
    def delete(self):
        data = request.get_json()
        return_data = ''
        states_code, message = DataBaseUtils.delete_node(node_id=data['id'])
        current_app.logger.warn('User: %s -> delete node : %s -> ret : %s,%s' % (
            session.get("username"), data, states_code, message))
        return jsonify({
            "code": states_code,
            "message": message,
            'data': return_data,
        })


class CalculatorView(MethodView):
    """
    激励计算器
    """

    @login_required
    def post(self):
        data = request.get_json()
        if not data.get('floor_price') or not data.get('price') or not data.get('number'):
            states_code, message = 400, '底价、售价和销售数量不能为空'
        else:
            ratio = float(Number.query_ratio(data['number']))
            if ratio == 0:
                states_code, message = 400, '数量 %s 的数量激励系数为0!' % data['number']
            else:
                if not data.get('percentage') and data.get('reward'):
                    data['percentage'] = float(data.get('reward')) / (
                            float(data.get('price')) - float(data.get('floor_price'))) / int(
                        data.get('number')) / ratio * 100
                    states_code, message = 200, '计算激励百分比'
                elif data.get('percentage') and not data.get('reward'):
                    data['reward'] = (float(data.get('price')) - float(data.get('floor_price'))) * float(
                        data.get('percentage'))/ 100 * int(data.get('number'))
                    states_code, message = 200, '计算总激励奖金'
                else:
                    states_code, message = 400, '激励百分比和总激励奖金需要且只需要填写一处'

        return jsonify({
            "code": states_code,
            "message": message,
            'data': data,
        })
