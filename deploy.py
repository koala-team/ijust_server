#!/usr/bin/env python
# -*- coding: utf-8 -*-
# find . -name \*.pyc -delete
__author__ = 'AminHP'

# python imports
import os
from mongoengine.connection import disconnect

# project imports
from project.application import create_app
from project.config import DeploymentConfig


disconnect()
config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "project/conf.py")
app = create_app(DeploymentConfig, "conf.py")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
