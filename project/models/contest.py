# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import os
import shutil

# project imports
from project import app
from project.extensions import db
from project.modules.datetime import utcnowts
from project.models.user import User
from project.models.team import Team


class Problem(db.Document):
    title = db.StringField(required=True)
    time_limit = db.FloatField(required=True)
    space_limit = db.IntField(required=True)

    meta = {
        'collection': 'problems'
    }

    @property
    def body_path(self):
        return os.path.join(app.config['PROBLEM_DIR'], str(self.pk))

    @property
    def testcase_dir(self):
        return os.path.join(app.config['TESTCASE_DIR'], str(self.pk))


    def delete(self, *args, **kwargs):
        if os.path.exists(self.body_path):
            os.remove(self.body_path)
        if os.path.exists(self.testcase_dir):
            shutil.rmtree(self.testcase_dir)
        super(Problem, self).delete(*args, **kwargs)


    def populate(self, json):
        if 'title' in json:
            self.title = json['title']
        if 'time_limit' in json:
            self.time_limit = json['time_limit']
        if 'space_limit' in json:
            self.space_limit = json['space_limit']


    def to_json(self):
        return dict(
            id = str(self.pk),
            title = self.title,
            time_limit = self.time_limit,
            space_limit = self.space_limit
        )


    def to_json_abs(self):
        return dict(
            id = str(self.pk),
            title = self.title
        )



class Result(db.Document):
    teams = db.DictField()
    sorted_team_ids = db.ListField(db.StringField())
    last_time_result_changed = db.FloatField(default=0)

    default_team_data = dict(
        problems = {},
        solved_count = 0,
        penalty = 0
    )

    default_problem_data = dict(
        submitted_at = None,
        failed_tries = 0,
        penalty = 0,
        solved = False
    )

    meta = {
        'collection': 'results'
    }


    @staticmethod
    def _make_query_ids(tid, pid):
        tqid = "teams__%s" % tid
        pqid = "teams__%s__problems__%s" % (tid, pid)
        return tqid, pqid


    def _check_existence(self, tid, pid):
        tqid, pqid = self._make_query_ids(tid, pid)

        find_query = {
            "pk": str(self.pk),
            tqid: None
        }
        update_query = {
            tqid: self.default_team_data,
            "add_to_set__sorted_team_ids": tid
        }
        Result.objects(**find_query).update(**update_query)

        update_query = {("set__%s" % pqid): self.default_problem_data}
        find_query = {
            "pk": str(self.pk),
            pqid: None
        }
        Result.objects(**find_query).update(**update_query)


    def _sort(self, last_time_result_changed):

        def compare(tid1, tid2):
            r1 = teams[tid1]
            r2 = teams[tid2]
            if r1["solved_count"] == r2["solved_count"]:
                return r1["penalty"] - r2["penalty"]
            return r2["solved_count"] - r1["solved_count"]

        aggregate_query = [
            {
                "$match": {
                    "_id": self.pk
                }
            },
            {
                "$project": {
                    "teams": "$teams",
                    "sorted_team_ids": "$sorted_team_ids"
                }
            }
        ]

        aggregated_result = list(Result.objects.aggregate(*aggregate_query))[0]
        teams = aggregated_result['teams']
        sorted_team_ids = aggregated_result['sorted_team_ids']
        sorted_team_ids.sort(cmp=compare)

        find_query = {
            "pk": str(self.pk),
            "last_time_result_changed": last_time_result_changed
        }
        Result.objects(**find_query).update(set__sorted_team_ids=sorted_team_ids)


    def update_failed_try(self, tid, pid, submitted_at, penalty=20):
        self._check_existence(tid, pid)
        tqid, pqid = self._make_query_ids(tid, pid)

        find_query = {
            "pk": str(self.pk),
            ("%s__solved" % pqid): False
        }
        update_query = {
            ("set__%s__submitted_at" % pqid): submitted_at,
            ("inc__%s__failed_tries" % pqid): 1,
            ("inc__%s__penalty" % pqid): penalty
        }
        Result.objects(**find_query).update(**update_query)


    def update_succeed_try(self, tid, pid, submitted_at, contest_starts_at):
        self._check_existence(tid, pid)
        tqid, pqid = self._make_query_ids(tid, pid)

        find_query = {
            "pk": str(self.pk),
            ("%s__solved" % pqid): False
        }
        update_query = {
            ("set__%s__submitted_at" % pqid): submitted_at,
            ("set__%s__solved" % pqid): True,
            ("inc__%s__penalty" % pqid): (submitted_at - contest_starts_at) // 60,
            ("inc__%s__solved_count" % tqid): 1
        }

        if Result.objects(**find_query).update(**update_query):
            aggregate_query = [
                {
                    "$match": {
                        "_id": self.pk
                    }
                },
                {
                    "$project": {
                        "last_penalty": ("$teams.%s.problems.%s.penalty" % (tid, pid))
                    }
                }
            ]
            aggregated_result = list(Result.objects.aggregate(*aggregate_query))[0]
            last_penalty = aggregated_result['last_penalty']
            last_time_result_changed = utcnowts(microseconds=True)
            update_query = {
                ("inc__%s__penalty" % tqid): last_penalty,
                "set__last_time_result_changed": last_time_result_changed
            }

            Result.objects(pk=str(self.pk)).update(**update_query)
            self._sort(last_time_result_changed)



class Contest(db.Document):
    name = db.StringField(required=True, unique=True)
    owner = db.ReferenceField('User', required=True)
    admins = db.ListField(db.ReferenceField('User'))
    created_at = db.IntField(required=True, default=lambda: utcnowts())
    starts_at = db.IntField(required=True)
    ends_at = db.IntField(required=True)
    pending_teams = db.ListField(db.ReferenceField('Team', reverse_delete_rule=db.PULL))
    accepted_teams = db.ListField(db.ReferenceField('Team', reverse_delete_rule=db.PULL))
    problems = db.ListField(db.ReferenceField('Problem', reverse_delete_rule=db.PULL))
    result = db.ReferenceField('Result')

    meta = {
        'collection': 'contests',
        'indexes': [
            '-starts_at',
            'owner',
            'admins',
            'pending_teams',
            'accepted_teams',
            'problems'
        ]
    }


    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if document.result:
            return
        result_obj = Result()
        result_obj.save()
        document.result = result_obj
        document.save()


    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        if document.result:
            document.result.delete()


    def save(self):
        if not (self.created_at < self.starts_at < self.ends_at):
            raise ContestDateTimeError()
        super(Contest, self).save()


    def is_user_in_contest(self, user_obj):
        for team in self.accepted_teams:
            if team.is_user_in_team(user_obj):
                return True
        return False


    def user_joining_status(self, user_obj):
        for team in self.accepted_teams:
            if team.is_user_in_team(user_obj):
                return 2, team
        for team in self.pending_teams:
            if team.is_user_in_team(user_obj):
                return 1, team
        return 0, None


    def populate(self, json):
        if 'name' in json:
            self.name = json['name']
        if 'starts_at' in json:
            self.starts_at = json['starts_at']
        if 'ends_at' in json:
            self.ends_at = json['ends_at']


    def to_json(self):
        return dict(
            id = str(self.pk),
            name = self.name,
            owner = self.owner.to_json_abs(),
            created_at = self.created_at,
            starts_at = self.starts_at,
            ends_at = self.ends_at,
            is_active = True if self.starts_at <= utcnowts() <= self.ends_at else False,
            is_ended = True if self.ends_at < utcnowts() else False,
            pending_teams_num = len(self.pending_teams),
            accepted_teams_num = len(self.accepted_teams)
        )


    def to_json_user(self, user_obj):
        json = self.to_json()
        status, team = self.user_joining_status(user_obj)
        json['joining_status'] = dict(
            status=status,
            team=team.to_json_abs() if team else None
        )
        json['is_owner'] = user_obj == self.owner
        json['is_admin'] = user_obj in self.admins
        return json


    def to_json_admins(self):
        return dict(
            admins = [admin.to_json_abs() for admin in self.admins]
        )


    def to_json_teams(self, category):
        if category == 'pending':
            return dict(
                pending_teams = [team.to_json() for team in self.pending_teams]
            )
        elif category == 'accepted':
            return dict(
                accepted_teams = [team.to_json() for team in self.accepted_teams]
            )
        else:
            return dict(
                pending_teams = [team.to_json() for team in self.pending_teams],
                accepted_teams = [team.to_json() for team in self.accepted_teams]
            )


    def to_json_problems(self):
        return dict(
            problems = [prob.to_json_abs() for prob in self.problems]
        )


    def to_json_result(self):
        sorted_teams = [Team.objects.get(pk=tid) for tid in self.result.sorted_team_ids]
        accepted_teams = set(self.accepted_teams)

        all_teams = [t for t in sorted_teams if t in accepted_teams]
        all_teams += accepted_teams.difference(sorted_teams)
        all_teams = [dict(id=str(t.pk), name=t.name) for t in all_teams]

        return dict(
            result = self.result.teams,
            teams = all_teams,
            problems = [p.to_json_abs() for p in self.problems]
        )


db.post_save.connect(Contest.post_save, sender=Contest)
db.pre_delete.connect(Contest.pre_delete, sender=Contest)



class ContestDateTimeError(db.ValidationError):
    pass
