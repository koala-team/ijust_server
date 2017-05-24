# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
from good import Schema, All, Any, Required, Optional, Length, Range, Match, Default

# project imports
from project.modules.recaptcha_validator import ReCaptcha


create_schema = Schema({
    Required('name'): All(unicode, Length(min=1, max=32)),
    Required('starts_at'): int,
    Required('ends_at'): int,
    Required('recaptcha'): ReCaptcha()
})


edit_schema = Schema({
    Optional('name'): All(unicode, Length(min=1, max=32)),
    Optional('starts_at'): int,
    Optional('ends_at'): int
})



team_join_schema = Schema({
    Required('team_id'): unicode
})



problem_create_schema = Schema({
    Required('title'): All(unicode, Length(min=1, max=32)),
    Required('time_limit'): All(Any(float, int), Range(min=0.1, max=10.0)),
    Required('space_limit'): All(int, Range(min=16, max=256))
})


problem_edit_schema = Schema({
    Optional('title'): All(unicode, Length(min=1, max=32)),
    Optional('time_limit'): All(Any(float, int), Range(min=0.1, max=10.0)),
    Optional('space_limit'): All(int, Range(min=16, max=256))
})


problem_change_order_schema = Schema({
    Required('order'): [Schema(int)]
})



admin_add_schema = Schema({
    Required('username'): unicode
})
