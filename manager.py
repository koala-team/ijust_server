#!/usr/bin/env python
# -*- coding: utf-8 -*-
# find . -name \*.pyc -delete
__author__ = 'AminHP'

# python imports
import os
import sys
from virtualenv import main


def setup_venv():
    import venv_manager
    venv_manager.create()
    venv_manager.update()
    venv_manager.activate()


def setup_manager():
    from app_manager import manager
    manager.run()



if __name__ == '__main__':
    setup_venv()
    setup_manager()
