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
        if not data.get('method') or not data.get('model'):
            states_code, message = 400, '参数不能为空!'
        elif data['method'] == 'add':
            states_code, message = DataBaseUtils.add_model(data['model'])
        elif data['method'] == 'edit':
            if not data.get('model_id'):
                states_code, message = 400, '参数不能为空!'
            else:
                states_code, message = DataBaseUtils.edit_model(data['model_id'], data['model'])
        else:
            states_code, message = 400, 'method 字段无法识别.'
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
            exci = DataBaseUtils.get_way(model_id=request.args['model'])
            data["select_index"] = int(request.args.get('model'))
        else:
            exci = DataBaseUtils.get_way(model_id=1)  # 默认展示第一个option的策略
        if exci:
            data['exci'] = exci
        return render_template('admin/excitation.html', segment='admin_excitation', data=data)

    def post(self):
        data = request.get_json()
        return_data = ''
        if not data.get('method'):
            states_code, message = 404, 'Method not none.'
        elif data.get('method') == 'add':
            if not data.get('start_time') or not data.get('name') or not data.get('model'):
                states_code, message = 400, '参数不能为空!'
            else:
                time = DataBaseUtils.datepicker_2_datetime(data['start_time'])
                model = Model.query.filter_by(name=data['model']).first()
                if model:
                    data['model_id'] = model.id
                    states_code, message = DataBaseUtils.add_way(data['model_id'], data['name'], time)
                else:
                    states_code, message = 404, 'Not found.'
        elif data.get('method') == 'query':
            return_data = DataBaseUtils.query_nodes(data.get('id'))  # ToDo:添加根据way id 查询node信息的内容
            if return_data:
                states_code, message = 200, 'OK'
            else:
                states_code, message = 404, 'Not found.'
        elif data.get('method') == 'edit':
            if not data.get('start_time') or not data.get('name') or not data.get('id'):
                states_code, message = 400, '参数不能为空!'
            else:
                time = DataBaseUtils.datepicker_2_datetime(data['start_time'])
                states_code, message = DataBaseUtils.edit_way(data.get('id'), data.get('name'), time)
        else:
            states_code, message = 400, 'Bad request.'
        return jsonify({
            "code": states_code,
            "message": message,
            'data': return_data,
        })

    def delete(self):
        data = request.get_json()
        states_code, message = DataBaseUtils.delete_way(data['id'])
        return jsonify({
            "code": states_code,
            "message": message,
            'data': '',
        })


class NodeView(MethodView):
    """
    节点管理页面
    """

    def get(self):
        data = {"models": DataBaseUtils.get_models(), "select_index": 1}
        if request.args.get('exci'):  # 指定策略
            model_index = DataBaseUtils.get_way(id=request.args.get('exci'))[0].model_id
            node = DataBaseUtils.query_nodes(request.args.get('exci'))
            data['exci'] = DataBaseUtils.get_way(model_id=model_index)
            data["select_index"] = model_index
            data["select_index2"] = int(request.args.get('exci'))
        else:
            if request.args.get('model'):  # 指定型号
                if not DataBaseUtils.get_way(model_id=request.args['model']):  # 型号未创建策略
                    data['exci'] = [{"id": 0, "name": "请先创建策略！"}]
                    data["select_index2"] = 0
                    node = []
                else:
                    exci_index = DataBaseUtils.get_way(model_id=request.args['model'])[0].id
                    node = DataBaseUtils.query_nodes(exci_index)
                    data['exci'] = DataBaseUtils.get_way(model_id=request.args['model'])
                    data["select_index2"] = int(exci_index)
                data["select_index"] = int(request.args.get('model'))
            else:  # 未指定型号
                exci_index = DataBaseUtils.get_way(model_id=1)[0].id
                node = DataBaseUtils.query_nodes(exci_index)
                data['exci'] = DataBaseUtils.get_way(model_id=1)
                data["select_index2"] = int(exci_index)
        if node:
            data["node"] = node
        return render_template('admin/node.html', segment='admin_node', data=data)

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
        elif data.get('method') == 'edit':
            states_code, message = DataBaseUtils.edit_node(data.get('node_id'), data.get('price'),
                                                           data.get('percentage'))
        else:
            states_code, message = 400, 'Bad request.'
        return jsonify({
            "code": states_code,
            "message": message,
            "data": return_data,
        })

    def delete(self):
        data = request.get_json()
        return_data = ''
        states_code, message = DataBaseUtils.delete_node(node_id=data['id'])
        return jsonify({
            "code": states_code,
            "message": message,
            'data': return_data,
        })
