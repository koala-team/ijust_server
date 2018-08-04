from project.modules.admin.base_view import BaseView
__author__ = 'SALAR'


class SubmissionView(BaseView):
    can_create = False
    form_excluded_columns = ['submitted_at', ]
