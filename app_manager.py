# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import os

# flask imports
from flask import Flask
from flask.ext.script import Manager

# project imports
from project.application import create_app
from project.config import DevelopmentConfig, DeploymentConfig, TestingConfig

manager = Manager(Flask('manager'))


@manager.command
def run():
    """
    Run server on port 8080 with default config.
    """
    app = create_app()
    app.run(host='0.0.0.0', port=8080)


@manager.command
def develop():
    """
    Run server on port 8080 with development config.
    """
    app = create_app(DevelopmentConfig)
    app.run(host='0.0.0.0', port=8080)


@manager.command
def deploy():
    """
    Run server on port 8080 with deployment config.
    """
    app = create_app(DeploymentConfig)
    app.run(host='0.0.0.0', port=8080)


@manager.command
def testing():
    """
    Run server on port 8080 with testing config.
    """
    app = create_app(TestingConfig)
    app.run(host='0.0.0.0', port=8080)


@manager.option(dest='config_file')
def custom_config(config_file):
    """
    Run server on port 8080 with custom config file.
    """
    app = create_app(config_file=os.path.abspath(config_file))
    app.run(host='0.0.0.0', port=8080)


@manager.command
def celery():
    """
    Run celery worker.
    """
    app = create_app()
    from mongoengine.connection import disconnect
    from project.extensions import celery
    from celery.bin import worker
    disconnect()
    worker = worker.worker(app=celery)
    worker.run()


@manager.option('-r', dest='resource', required=False, help='Resource name')
@manager.option('-u', dest='url', required=False, default='http://localhost:8080', help='Server url')
def test(resource, url):
    """
    Test api. You can specify a resource (like api_1.user) for single testing.
    By default all resources will be tested.
    """
    from tests import run
    run(url, resource)
