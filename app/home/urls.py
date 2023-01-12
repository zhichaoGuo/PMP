from .views import *

home.add_url_rule('/', view_func=RootView.as_view('root'))
home.add_url_rule('/login', view_func=LoginView.as_view('login'))
home.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
home.add_url_rule('/home', view_func=HomeView.as_view('home'))
