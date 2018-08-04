from project.modules.admin.base_view import BaseView

__author__ = 'SALAR'


class ContestView(BaseView):
    form_excluded_columns = ["created_at", "pending_teams", "Result"]
    column_exclude_list = ["accepted_teams", ]


class ProblemView(BaseView):
    pass
