#!/usr/bin/env python
# -*- coding: utf-8 -*-
# find . -name \*.pyc -delete
__author__ = 'AminHP'

# python imports
import os
from mongoengine.connection import disconnect
from celery.bin import worker

# project imports
from deploy import app
from project.extensions import celery


disconnect()
worker = worker.worker(app=celery)

if __name__ == '__main__':
    worker.run()
