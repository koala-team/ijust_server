# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import os
import shutil
from enum import Enum

# project imports
from project import app
from project.extensions import db
from project.models.user import User
from project.models.team import Team
from project.models.contest import Contest, Problem, Result
from project.modules.datetime import utcnowts
from project.modules.fields import IntEnumField
from project.modules.ijudge.types import JudgementStatusType, ProgrammingLanguageType


class Submission(db.Document):
    filename = db.StringField(required=True)
    prog_lang = IntEnumField(enum=ProgrammingLanguageType, required=True)
    submitted_at = db.IntField(required=True, default=lambda: utcnowts())

    contest = db.ReferenceField('Contest', required=True, reverse_delete_rule=db.CASCADE)
    problem = db.ReferenceField('Problem', required=True, reverse_delete_rule=db.CASCADE)
    team = db.ReferenceField('Team', reverse_delete_rule=db.CASCADE)
    user = db.ReferenceField('User', required=True)

    status = IntEnumField(enum=JudgementStatusType, required=True, default=JudgementStatusType.Pending)
    reason = db.StringField()

    meta = {
        'collection': 'submissions',
        'indexes': [
            '-submitted_at',
            'contest',
            ('contest', 'team'),
            ('contest', 'problem'),
            ('contest', 'problem', 'team')
        ]
    }

    @property
    def data_dir(self):
        return os.path.join(
            app.config['SUBMISSION_DIR'],
            str(self.contest.pk),
            str(self.problem.pk),
            str(self.team.pk) if self.team else 'test',
            str(self.submitted_at)
        )

    @property
    def code_path(self):
        return os.path.join(
            self.data_dir,
            self.filename
        )


    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        if os.path.exists(document.data_dir):
            shutil.rmtree(document.data_dir)


    def populate(self, json):
        self.filename = json['filename']
        self.prog_lang = json['prog_lang']


    def to_json(self):
        return dict(
            id = str(self.pk),
            filename = self.filename,
            prog_lang = self.prog_lang.name,
            submitted_at = self.submitted_at,
            problem = self.problem.to_json_abs(),
            user = self.user.to_json_abs(),
            status = self.status.name,
            reason = self.reason
        )


db.pre_delete.connect(Submission.pre_delete, sender=Submission)
