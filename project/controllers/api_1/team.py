# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# flask imports
from flask import jsonify, request, g, abort

# project imports
from project import app
from project.extensions import db, auth
from project.models.team import Team
from project.models.user import User
from project.models.contest import Contest


@app.api_route('', methods=['POST'])
@app.api_validate('team.create_schema')
@auth.authenticate
def create():
    """
    Create Team
    Maximum number of teams can be created is 5
    ---
    tags:
      - team
    parameters:
      - name: body
        in: body
        description: Team information
        required: true
        schema:
          id: TeamCreation
          required:
            - name
          properties:
            name:
              type: string
              example: babyknight
              minLength: 1
              maxLength: 32
            members:
              type: array
              maxLength: 2
              items:
                type: string
                description: Member username
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      201:
        description: Successfully created
        schema:
          $ref: "#/definitions/api_1_team_info_get_TeamInfo"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      404:
        description: Member does not exist
      406:
        description: You can't create more teams
      409:
        description: Team already exists
    """

    json = request.json
    try:
        owner = User.objects.get(pk=g.user_id)
        my_teams = Team.teams(owner)
        if len(my_teams['owner_teams']) >= 5:
            return abort(406, "You can't create more teams")

        obj = Team(name=json['name'])
        obj.owner = owner
        obj.populate(json)
        obj.save()
        return jsonify(obj.to_json()), 201

    except db.NotUniqueError:
        return abort(409, "Team already exists")
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Member does not exist")


@app.api_route('<string:tid>', methods=['GET'])
@auth.authenticate
def info(tid):
    """
    Get Team Info
    ---
    tags:
      - team
    parameters:
      - name: tid
        in: path
        type: string
        required: true
        description: Id of team
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Team information
        schema:
          id: TeamInfo
          type: object
          properties:
            id:
              type: string
              description: Team id
            name:
              type: string
              description: Team name
            owner:
              description: Owner info
              schema:
                  id: UserAbsInfo
                  type: object
                  properties:
                    id:
                      type: string
                      description: Member id
                    username:
                      type: string
                      description: Member username
            members:
              type: array
              items:
                schema:
                  $ref: "#/definitions/api_1_team_info_get_UserAbsInfo"
      401:
        description: Token is invalid or has expired
      404:
        description: Team does not exist
    """

    try:
        obj = Team.objects.get(pk=tid)
        return jsonify(obj.to_json()), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort('404, Team does not exist')


@app.api_route('<string:tid>', methods=['PUT'])
@app.api_validate('team.edit_schema')
@auth.authenticate
def edit(tid):
    """
    Edit Team
    ---
    tags:
      - team
    parameters:
      - name: tid
        in: path
        type: string
        required: true
        description: Id of team
      - name: body
        in: body
        description: Team information
        required: true
        schema:
          id: TeamEdition
          properties:
            name:
              type: string
              example: babyknight
              minLength: 1
              maxLength: 32
            members:
              type: array
              maxLength: 2
              items:
                type: string
                description: Member username
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully edited
        schema:
          $ref: "#/definitions/api_1_team_info_get_TeamInfo"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner of the team
      404:
        description: Team or Member does not exist
      409:
        description: Team name already exists
    """

    json = request.json
    try:
        obj = Team.objects.get(pk=tid)
        if str(obj.owner.pk) != g.user_id:
            return abort(403, "You aren't owner of the team")

        obj.populate(json)
        obj.save()
        return jsonify(obj.to_json()), 200

    except db.NotUniqueError:
        return abort(409, "Team name already exists")
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Member does not exist")



@app.api_route('', methods=['GET'])
@auth.authenticate
def list():
    """
    Get My Teams
    ---
    tags:
      - team
    parameters:
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Team informations
        schema:
          id: TeamInfos
          type: object
          properties:
            owner_teams:
              type: array
              items:
                schema:
                  $ref: "#/definitions/api_1_team_info_get_TeamInfo"
            member_teams:
              type: array
              items:
                schema:
                  $ref: "#/definitions/api_1_team_info_get_TeamInfo"
      401:
        description: Token is invalid or has expired
    """

    user_obj = User.objects.get(pk=g.user_id)
    teams = Team.teams(user_obj)
    return jsonify(teams), 200


@app.api_route('<string:tid>', methods=['DELETE'])
@auth.authenticate
def delete(tid):
    """
    Team Delete
    ---
    tags:
      - team
    parameters:
      - name: tid
        in: path
        type: string
        required: true
        description: Id of team
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully deleted
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner of the team
      404:
        description: Team does not exist
      406:
        description: The team has participated in a number of contests
    """

    try:
        obj = Team.objects.get(pk=tid)
        user_obj = User.objects.get(pk=g.user_id)

        if user_obj != obj.owner:
            return abort(403, "You aren't owner of the team")

        if Contest.objects(accepted_teams=obj).count() > 0:
            return abort(406, "The team has participated in a number of contests")

        obj.delete()
        return '', 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Team does not exist")
