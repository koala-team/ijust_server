from wtforms import PasswordField
from project.modules.admin.base_view import BaseView
__author__ = 'SALAR'


class UserView(BaseView):
    column_exclude_list = ['password', ]

    form_overrides = {
        'password': PasswordField
    }

    column_formatters = {'password': lambda v, c, m, p: m.password is not None}
