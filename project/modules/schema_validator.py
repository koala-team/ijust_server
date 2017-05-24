# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import os
import imp
import pkgutil
from functools import wraps
from good import Schema, Invalid
import collections

# flask imports
from flask import request, abort


class Validator(object):
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)


    def init_app(self, app):
        self.dir = app.config['SCHEMA_DIR']
        self.app = app

        self.load_schemas()
        app.validate = self.validate_schema
        app.api_validate = self.api_validate_schema


    def load_schemas(self):
        schemas = {}

        for root, dirnames, filenames in os.walk(self.dir):
            for file in filenames:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    module = imp.load_source(root, path)
                    for each in dir(module):
                        attr = getattr(module, each)
                        if isinstance(attr, Schema):
                            name = path[:-3].replace(self.dir, '').split('/')[1:]
                            schema_name = '.'.join(name + [each])
                            schemas[schema_name] = attr

        self.schemas = schemas


    def validate_schema(self, schema_name, api=False):
        def wrapper(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                api_dir = ''
                if api:
                    api_dir = "%s." % f.__module__.split('.')[2]
                schema = self.schemas[api_dir + schema_name]
                #########################
                json = request.json or {}
                try:
                    schema(json)
                except Invalid as ee:

                    def update(d, u):
                        for k, v in u.iteritems():
                            if isinstance(v, collections.Mapping):
                                r = update(d.get(k, {}), v)
                                d[k] = r
                            else:
                                d[k] = u[k]
                        return d

                    def get_errors():
                        errors = {}
                        for e in ee:
                            main = each = {}
                            for p in e.path:
                                prev = each
                                each[p] = {}
                                each = each[p]
                            prev[prev.keys()[0]] = e.message
                            update(errors, main)
                        return errors

                    return abort(400, get_errors())

                return f(*args, **kwargs)
            return decorated
        return wrapper


    def api_validate_schema(self, schema_name):
        return self.validate_schema(schema_name, True)
