from app.excitation.views import *

excitation.add_url_rule('/all_record', view_func=ExcitationView.as_view('all_record'))
excitation.add_url_rule('/record', view_func=RecordView.as_view('record'))
excitation.add_url_rule('/detail', view_func=DetailView.as_view('detail'))
