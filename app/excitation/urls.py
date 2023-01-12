from app.excitation.views import excitation, ExcitationView

excitation.add_url_rule('/tables', view_func=ExcitationView.as_view('tables'))
