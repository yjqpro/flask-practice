from flask import (
    request,
    redirect,
    url_for)
from flask_login import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

class AuthenticationModelView(ModelView):
    __abstract__ = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class FooAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

    @expose('/')
    def index(self):
        return self.render('admin/index.html')

