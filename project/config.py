# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import random
import string
import os


class DefaultConfig(object):
    # app

    DEFAULT_APP_NAME = 'ijust'
    DEBUG = True
    TESTING = True
    DEPLOYMENT = False
    TOKEN_EXPIRE_TIME = 5 * 3600

    # directory

    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) # don't touch this !!!

    SCHEMA_DIR = os.path.join(BASE_DIR, 'schemas')
    DATA_DIR = os.path.join(BASE_DIR, '..', '..', 'Data')
    TEMP_DIR = os.path.join(DATA_DIR, 'Temp')
    MEDIA_DIR = os.path.join(DATA_DIR, 'Media')
    PROBLEM_DIR = os.path.join(MEDIA_DIR, 'Problems')
    TESTCASE_DIR = os.path.join(MEDIA_DIR, 'Testcases')
    SUBMISSION_DIR = os.path.join(MEDIA_DIR, 'Submissions')

    # form

    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False

    # upload

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # pagination

    DEFAULT_PAGE_SIZE = 10

    # cache

    CACHE_TYPE = 'null'
    CACHE_DEFAULT_TIMEOUT = 900
    CACHE_THRESHOLD = 100
    CACHE_NO_NULL_WARNING = True
    CACHE_DIR = os.path.join(TEMP_DIR, 'Cache')

    # redis

    REDIS_URL = "redis://localhost:6379/0"

    # celery

    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # mongo

    MONGODB_SETTINGS = {
        'db': 'ijust',
        'host': 'localhost',
        'port': 27017
    }

    # recaptcha

    RECAPTCHA_ENABLED = False
    RECAPTCHA_SITE_KEY = "6LeDPwcTAAAAADVt4vp-kdTHXcbl76JbRFK3PUV5"
    RECAPTCHA_SECRET_KEY = "6LeDPwcTAAAAAKF5mXqJpKqo1NW2nntCrjyFwi3Q"


class DevelopmentConfig(DefaultConfig):
    # app

    TESTING = False

    # cache

    CACHE_TYPE = 'filesystem'

    # recaptcha

    RECAPTCHA_ENABLED = True


class DeploymentConfig(DefaultConfig):
    # app

    DEBUG = False
    DEPLOYMENT = True
    TOKEN_EXPIRE_TIME = 10 * 24 * 3600

    # cache

    CACHE_TYPE = 'redis'

    # recaptcha

    RECAPTCHA_ENABLED = True


class TestingConfig(DefaultConfig):
    # app

    DEBUG = True
    TESTING = True

    # cache

    CACHE_TYPE = 'filesystem'

    # recaptcha

    RECAPTCHA_ENABLED = False
