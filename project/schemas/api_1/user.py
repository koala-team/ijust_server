# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
from good import Schema, All, Required, Optional, Length, Match, Email

# project imports
from project.modules.recaptcha_validator import ReCaptcha


signup_schema = Schema({
    Required('username'): All(unicode, Match(r'^[a-zA-Z0-9_]*$'), Length(min=1, max=32)),
    Required('email'): Email(),
    Required('password'): All(unicode, Length(min=3, max=32)),
    Required('recaptcha'): ReCaptcha()
})


login_schema = Schema({
    Required('login'): unicode,
    Required('password'): unicode
})


edit_schema = Schema({
    Optional('email'): Email(),
    Optional('password'): Schema({
        Required('old_password'): All(unicode, Length(min=3, max=32)),
        Required('new_password'): All(unicode, Length(min=3, max=32))
    }),
    Optional('firstname'): All(unicode, Length(min=1, max=32)),
    Optional('lastname'): All(unicode, Length(min=1, max=32))
})