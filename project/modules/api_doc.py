# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import os

# flask imports
from flasgger import Swagger


class ApiDoc(object):
    def __init__(self, app=None):
        self.app = app
        self.swagger = Swagger()

        if app:
            self.init_app(app)


    def init_app(self, app):
        self.app = app

        app.config['SWAGGER'] = {
            "swagger_version": "2.0",
            "headers": [],
            "specs": self.get_specs()
        }
        self.swagger.init_app(self.app)


    def get_specs(self):

        def get_spec_config(api):
            ver = '_'.join(api.split('_')[1:])
            return dict(version=ver,
                        title='Api v' + ver,
                        endpoint='spec_' + api,
                        route='/docs/api/v%s' % ver,
                        rule_filter=lambda rule: rule.endpoint.startswith(api))

        return [get_spec_config(api) for api in self.find_apis()]


    def find_apis(self):
        path = os.path.join(self.app.config['BASE_DIR'], 'controllers')
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) and name.startswith('api')]
