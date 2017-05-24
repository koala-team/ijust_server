# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# project imports
from project.extensions import db
from project.models.user import User


class Team(db.Document):
    name = db.StringField(required=True, unique=True)
    owner = db.ReferenceField('User', required=True)
    members = db.ListField(db.ReferenceField('User'))

    meta = {
        'collection': 'teams',
        'indexes': [
            'name',
            'owner',
            'members'
        ]
    }


    @classmethod
    def teams(cls, user_obj):
        owner_teams = cls.objects.filter(owner=user_obj)
        owner_teams = [t.to_json() for t in owner_teams]
        member_teams = cls.objects.filter(members=user_obj)
        member_teams = [t.to_json() for t in member_teams]
        return dict(owner_teams=owner_teams, member_teams=member_teams)


    def is_user_in_team(self, user_obj):
        return user_obj == self.owner or user_obj in self.members


    def populate(self, json):
        if 'name' in json:
            self.name = json['name']
        if 'members' in json:
            members = filter(lambda un: un != self.owner.username, json['members'])
            self.members = [User.objects.get(username=username) for username in members]


    def to_json(self):
        return dict(
            id = str(self.pk),
            name = self.name,
            owner = self.owner.to_json_abs(),
            members = [user.to_json_abs() for user in self.members]
        )


    def to_json_abs(self):
        return dict(
            id = str(self.pk),
            name = self.name,
            owner = self.owner.to_json()
        )
