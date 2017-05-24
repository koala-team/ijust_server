# -*- coding: utf-8 -*-
__author__ = 'AminHP'


class ApiRouter(object):
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)


    def init_app(self, app):
        self.app = app
        app.api_route = self.api_route


    def api_route(self, rule, **options):
        def decorator(f):
            mod = f.__module__.split('.')
            api_version = '_'.join(mod[2].split('_')[1:])
            resource = mod[3]
            ####################
            new_rule = '/api/v%s/%s/%s' % (api_version, resource, rule)
            endpoint = options.pop('endpoint', None)
            if not endpoint:
                endpoint = "%s.%s" % ('.'.join(f.__module__.split('.')[2:]), f.__name__)
            new_rule = new_rule[:-1] if new_rule.endswith('/') else new_rule
            self.app.add_url_rule(new_rule, endpoint, f, **options)
            return f
        return decorator
