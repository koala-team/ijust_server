# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
from time import time


def utcnowts(microseconds=False):
    if microseconds:
        return time()
    return int(time())
