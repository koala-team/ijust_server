# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import os
import fnmatch

# project imports
from venv_manager import pyresttest


DIR = __path__[0]
EXT = 'yaml'


def run(url, resource=None):
    if not resource:
        run_all(url)
        return

    test = '%s.%s' % (os.path.join(DIR, resource.replace('.', '/')), EXT)
    command_run(url, test)


def run_all(url):
    tests = []
    for root, dirnames, filenames in os.walk(DIR):
        for filename in fnmatch.filter(filenames, '*.%s' % EXT):
            tests.append(os.path.join(root, filename))
    for t in tests:
        command_run(url, t)


def command_run(url, test_file):
    pyresttest([url, test_file])
