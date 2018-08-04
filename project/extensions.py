# -*- coding: utf-8 -*-
__author__ = ['AminHP', 'SALAR']

# flask extentions
from flask_cache import Cache
from flask_celery import Celery
from flask_redis import FlaskRedis
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from flask_admin import Admin

# project extentions
from project.modules.schema_validator import Validator
from project.modules.api_router import ApiRouter
from project.modules.api_doc import ApiDoc
from project.modules.auth import Auth
from project.modules.recaptcha import ReCaptcha


cache = Cache()
celery = Celery()
redis = FlaskRedis()
db = MongoEngine()
cors = CORS(resources={r"/api/*": {"origins": "*"}})
validator = Validator()
api_router = ApiRouter()
api_doc = ApiDoc()
auth = Auth(redis)
recaptcha = ReCaptcha()
admin = Admin(template_mode='bootstrap3', url='/admin')
