# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
from good import Schema, Invalid

# project imports
from project.extensions import recaptcha


class ReCaptcha(object):

    def __call__(self, response):
        if recaptcha.verify(response):
            return response
        raise Invalid("wrong captcha")
