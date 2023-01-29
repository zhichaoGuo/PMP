from app.admin.views import admin, ExcitationView, ModelView, GlobalView, NodeView, CalculatorView

admin.add_url_rule('/admin_global', view_func=GlobalView.as_view('global'))
admin.add_url_rule('/admin_model', view_func=ModelView.as_view('model'))
admin.add_url_rule('/admin_excitation', view_func=ExcitationView.as_view('excitation'))
admin.add_url_rule('/admin_node', view_func=NodeView.as_view('node'))
admin.add_url_rule('/calculator', view_func=CalculatorView.as_view('calculator'))
