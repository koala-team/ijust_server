# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# flask extentions
from flask.ext.cache import Cache
from flask.ext.celery import Celery
from flask.ext.redis import FlaskRedis
from flask.ext.mongoengine import MongoEngine
from flask.ext.cors import CORS

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
