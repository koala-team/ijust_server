from flask_admin.contrib.mongoengine import ModelView
__author__ = 'SALAR'


class BaseView(ModelView):
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_set_page_size = True
    can_view_details = True
