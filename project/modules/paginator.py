# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import json as pyjson
from functools import wraps
from cStringIO import StringIO as IO

# flask imports
from flask import request, url_for, jsonify
from flask.ext.mongoengine.pagination import Pagination

# project imports
from project import app
from project.extensions import db


def paginate(key, max_per_page, **pkwargs):

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            query, result_func = f(*args, **kwargs)

            page = request.args.get('page', 1, type=int)
            per_page = min(
                request.args.get('per_page', app.config['DEFAULT_PAGE_SIZE'], type=int),
                max_per_page
            )

            if not isinstance(query, db.QuerySet):
                return f(*args, **kwargs)

            pagination_obj = Pagination(query, page, per_page)
            meta = {
                'page': pagination_obj.page,
                'per_page': pagination_obj.per_page,
                'total': pagination_obj.total,
                'pages': pagination_obj.pages
            }

            if pagination_obj.has_prev:
                meta['prev'] = url_for(
                    request.endpoint,
                    page = pagination_obj.prev_num,
                    per_page = per_page,
                    _external=True,
                    **kwargs
                )
            else:
                meta['prev'] = None

            if pagination_obj.has_next:
                meta['next'] = url_for(
                    request.endpoint,
                    page = pagination_obj.next_num,
                    per_page=per_page,
                    _external=True,
                    **kwargs
                )
            else:
                meta['next'] = None

            meta['first'] = url_for(
                request.endpoint,
                page = 1,
                per_page = per_page,
                _external = True,
                **kwargs
            )

            meta['last'] = url_for(
                request.endpoint,
                page = pagination_obj.pages,
                per_page=per_page,
                _external=True,
                **kwargs
            )

            return jsonify({
                str(key): [result_func(item) for item in pagination_obj.items],
                'meta': meta
            })

        return wrapped

    return decorator
