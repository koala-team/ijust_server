# -*- coding: utf-8 -*-
__author__ = 'AminHP'

from good import Schema, All, Any, Required, Optional, Length, Match, Default


create_schema = Schema({
    Required('name'): All(unicode, Length(min=1, max=32)),
    Required('members'): Any(All([Schema(unicode)], Length(max=2)), Default([]))
})


edit_schema = Schema({
    Optional('name'): All(unicode, Length(min=1, max=32)),
    Optional('members'): All([Schema(unicode)], Length(max=2))
})
