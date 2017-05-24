# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import magic

# flask imports
from wtforms import FileField, StringField, IntegerField
from wtforms.validators import DataRequired, InputRequired, NumberRange
from flask.ext.wtf import FlaskForm

# project imports
from project.models.submission import ProgrammingLanguageType


class UploadCode(FlaskForm):
    contest_id = StringField(validators=[DataRequired()])
    problem_id = StringField(validators=[DataRequired()])
    team_id = StringField(validators=[], default=None)
    prog_lang = IntegerField(validators=[InputRequired(), NumberRange(min=0, max=len(ProgrammingLanguageType)-1)])
    code = FileField(validators=[DataRequired()])
    #allowed_extensions = ['text/plain', 'text/x-c', 'text/x-java-source', 'text/x-script.pyhton']


    def validate_file(self):
        data = self.code.data.read(16)
        self.code.data.seek(0)

        #if not magic.from_buffer(data, mime=True) in self.allowed_extensions:
        #    return False
        #return True
        return magic.from_buffer(data, mime=True).startswith('text/')


    def to_json(self):
        return dict(
            filename = self.code.raw_data[0].filename.replace(' ', '_'),
            contest_id = self.contest_id.data,
            problem_id = self.problem_id.data,
            team_id = self.team_id.data,
            prog_lang = self.prog_lang.data
        )
