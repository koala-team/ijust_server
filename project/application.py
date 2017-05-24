# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import os

# flask imports
from flask import Flask, jsonify

# project imports
from config import DefaultConfig


def create_app(config_obj=DefaultConfig, config_file=None):
    app = Flask(__name__)
    configure_app(app, config_obj, config_file)
    configure_extensions(app)
    configure_errorhandlers(app)
    install_app(app)
    return app


def install_app(app):
    import flask
    import project
    import controllers

    project.app = app
    flask.current_app = app
    for module in controllers.__all__:
        __import__('project.controllers.%s' % module)


def configure_app(app, config_obj, config_file):
    if config_obj:
        app.config.from_object(config_obj)
    if config_file:
        app.config.from_pyfile(config_file)

    [os.makedirs(v) for k, v in app.config.items() if k.endswith('DIR') and not os.path.exists(v)]


def configure_extensions(app):
    from project import extensions

    for extension in dir(extensions):
        try:
            attr = getattr(extensions, extension)
            if not isinstance(attr, type) and 'init_app' in dir(attr):
                attr.init_app(app)
        except AttributeError as e:
            print e


def configure_errorhandlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify(error=error.description), 400) if app.config['DEBUG'] else ("", 400)

    @app.errorhandler(401)
    def unauthorized(error):
        return (jsonify(error=error.description), 401) if app.config['DEBUG'] else ("", 401)

    @app.errorhandler(403)
    def forbidden(error):
        return (jsonify(error=error.description), 403) if app.config['DEBUG'] else ("", 403)

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify(error=error.description), 404) if app.config['DEBUG'] else ("", 404)

    @app.errorhandler(406)
    def not_acceptable(error):
        return (jsonify(error=error.description), 406) if app.config['DEBUG'] else ("", 406)

    @app.errorhandler(409)
    def conflict(error):
        return (jsonify(error=error.description), 409) if app.config['DEBUG'] else ("", 409)

    @app.errorhandler(413)
    def entity_too_large(error):
        desc = "Request entity too large. (max is 4mg)"
        return (jsonify(error=desc), 413) if app.config['DEBUG'] else ("", 413)

    @app.errorhandler(415)
    def unsupported_media_type(error):
        return (jsonify(error=error.description), 415) if app.config['DEBUG'] else ("", 415)
