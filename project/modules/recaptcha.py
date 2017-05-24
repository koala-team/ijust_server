# -*- coding: utf-8 -*-
__author__ = 'AminHP'

#python imports
import requests


class ReCaptcha(object):
    url = "https://www.google.com/recaptcha/api/siteverify"

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.enabled = app.config['RECAPTCHA_ENABLED']
        self.site_key = app.config['RECAPTCHA_SITE_KEY']
        self.secret_key = app.config['RECAPTCHA_SECRET_KEY']
        self.app = app


    def get_site_key(self):
        return self.site_key


    def verify(self, response):
        if not self.enabled:
            return True

        data = {
            "secret": self.secret_key,
            "response": response
        }

        r = requests.get(self.url, params=data)
        return r.json()['success'] and r.status_code == 200
