# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
from functools import wraps

# flask imports
from flask import request, abort, g
from uuid import uuid4


class Auth(object):
    def __init__(self, redis_connection, app=None):
        self.redis = redis_connection
        self.app = app
        if app:
            self.init_app(app)


    def init_app(self, app):
        self.app = app
        self.token_expire_time = self.app.config['TOKEN_EXPIRE_TIME']


    def generate_token(self, user_id):
        token = str(uuid4())
        self.redis.setex(token, user_id, self.token_expire_time)
        return token


    def expire_token(self):
        self.redis.delete(request.headers['Access-Token'])


    def authenticate(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):

            if not 'Access-Token' in request.headers:
                return abort(401, "Set token to access protected routes")

            token = request.headers['Access-Token']
            user_id = self.redis.get(token)

            if not user_id:
                return abort(401, "Token is invalid or has expired")

            g.user_id = user_id
            return f(*args, **kwargs)

        return decorated
