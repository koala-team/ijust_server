# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import magic

# flask imports
from wtforms import FileField
from wtforms.validators import DataRequired
from flask.ext.wtf import FlaskForm


class UploadProblemBody(FlaskForm):
    body = FileField(validators=[DataRequired()])
    allowed_extensions = ['application/pdf']

    def validate_file(self):
        data = self.body.data.read(16)
        self.body.data.seek(0)

        if not magic.from_buffer(data, mime=True) in self.allowed_extensions:
            return False
        return True


class UploadTestCase(FlaskForm):
    testcase = FileField(validators=[DataRequired()])
    allowed_extensions = ['application/zip']

    def validate_file(self):
        data = self.testcase.data.read(16)
        self.testcase.data.seek(0)

        if not magic.from_buffer(data, mime=True) in self.allowed_extensions:
            return False
        return True
