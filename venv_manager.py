# -*- coding: utf-8 -*-
__author__ = 'AminHP'

import os
import sys
from virtualenv import main


def create():
    if not os.path.isdir(venv_dir()):
        tmp = sys.argv
        sys.argv = ['', venv_dir()]
        main()
        sys.argv = tmp


def remove():
    if os.path.isdir(venv_dir()):
        command = 'rm -r %s' % venv_dir()
        os.system(command)


def activate():
    lib_dir = os.path.join(venv_dir(), 'lib/python2.7/site-packages')
    sys.path.append(lib_dir)


def deactivate():
    sys.path.pop()


def update():
    print 'Updating ...'
    req_dir = os.path.join(framework_dir(), 'requirements')
    pip(['install', '-r', req_dir, '>', '/dev/null'])



def pip(command_list):
    pip_cmd = os.path.join(venv_dir(), 'bin/pip')
    command = '%s %s' % (pip_cmd, ' '.join(command_list))
    os.system(command)


def pyresttest(command_list):
    prt_cmd = os.path.join(venv_dir(), 'bin/pyresttest')
    command = '%s %s' % (prt_cmd, ' '.join(command_list))
    if os.system(command) == 256:
        print '** USING GLOBAL PYRESTTEST **'
        prt_cmd = '/usr/bin/pyresttest'
        command = '%s %s' % (prt_cmd, ' '.join(command_list))
        if os.system(command) == 32512:
            print '* please install pyresttest:\n> sudo apt-get install python-pycurl\n> sudo pip install pyresttest'



def framework_dir():
    return os.path.abspath(os.path.dirname(__file__))


def venv_dir():
    return os.path.join(framework_dir(), 'venv')
