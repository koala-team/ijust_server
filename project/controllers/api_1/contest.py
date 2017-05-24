# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
import os
import shutil
import zipfile
import StringIO
import base64

# flask imports
from flask import jsonify, request, g, send_file, abort

# project imports
from project import app
from project.extensions import db, auth
from project.modules.datetime import utcnowts
from project.modules.paginator import paginate
from project.models.contest import Contest, Problem, ContestDateTimeError
from project.models.team import Team
from project.models.user import User
from project.forms.problem import UploadProblemBody, UploadTestCase


@app.api_route('', methods=['POST'])
@app.api_validate('contest.create_schema')
@auth.authenticate
def create():
    """
    Create Contest
    ---
    tags:
      - contest
    parameters:
      - name: body
        in: body
        description: Contest information
        required: true
        schema:
          id: ContestCreation
          required:
            - name
            - starts_at
            - ends_at
          properties:
            name:
              type: string
              example: babyknight
              minLength: 1
              maxLength: 32
            starts_at:
              type: integer
              description: Contest starts_at (utc timestamp)
            ends_at:
              type: integer
              description: Contest ends_at (utc timestamp)
            recaptcha:
              type: string
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      201:
        description: Successfully created
        schema:
          $ref: "#/definitions/api_1_contest_list_owner_get_ContestInfo"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      406:
        description: EndTime must be greater than StartTime and StartTime must be greater than CreationTime
      409:
        description: Contest already exists
    """

    json = request.json
    try:
        obj = Contest()
        obj.owner = User.objects.get(pk=g.user_id)
        obj.populate(json)
        obj.save()
        return jsonify(obj.to_json()), 201

    except db.NotUniqueError:
        return abort(409, "Contest already exists")
    except ContestDateTimeError:
        return abort(406, "EndTime must be greater than StartTime and StartTime must be greater than CreationTime")


@app.api_route('<string:cid>', methods=['GET'])
@auth.authenticate
def info(cid):
    """
    Get Contest Info
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Contest information
        schema:
          id: ContestInfoUser
          type: object
          properties:
            id:
              type: string
              description: Contest id
            name:
              type: string
              description: Contest name
            owner:
              description: Owner info
              schema:
                  id: ContestOwnerInfo
                  type: object
                  properties:
                    id:
                      type: string
                      description: Owner id
                    username:
                      type: string
                      description: Owner username
            created_at:
              type: integer
              description: Contest created_at (utc timestamp)
            starts_at:
              type: integer
              description: Contest starts_at (utc timestamp)
            ends_at:
              type: integer
              description: Contest ends_at (utc timestamp)
            is_active:
              type: boolean
              description: Contest is_active
            is_ended:
              type: boolean
              description: Contest is_ended
            is_owner:
              type: boolean
              description: Contest is_owner
            is_admin:
              type: boolean
              description: Contest is_admin
            pending_teams_num:
              type: integer
              description: Contest number of pending teams
            accepted_teams_num:
              type: integer
              description: Contest number of accepted teams
            joining_status:
              type: object
              description: Contest user joining status
              schema:
                properties:
                  status:
                    type: integer
                    description: joining status (0=not_joined, 1=waiting, 2=joined)
                  team:
                    schema:
                      id: TeamAbsInfo
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
                            $ref: "#/definitions/api_1_team_info_get_UserAbsInfo"
      401:
        description: Token is invalid or has expired
      404:
        description: Contest does not exist
    """

    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)
        return jsonify(obj.to_json_user(user_obj)), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


@app.api_route('<string:cid>', methods=['PUT'])
@app.api_validate('contest.edit_schema')
@auth.authenticate
def edit(cid):
    """
    Edit Contest
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: body
        in: body
        description: Contest information
        required: true
        schema:
          id: ContestEdition
          properties:
            name:
              type: string
              example: babyknight
              minLength: 1
              maxLength: 32
            starts_at:
              type: integer
              description: Contest starts_at (utc timestamp)
            ends_at:
              type: integer
              description: Contest ends_at (utc timestamp)
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully edited
        schema:
          $ref: "#/definitions/api_1_contest_list_owner_get_ContestInfo"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest does not exist
      406:
        description: EndTime must be greater than StartTime and StartTime must be greater than CreationTime
      409:
        description: Contest name already exists
    """

    json = request.json
    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        obj.populate(json)
        obj.save()
        return jsonify(obj.to_json()), 200

    except db.NotUniqueError:
        return abort(409, "Contest name already exists")
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")
    except ContestDateTimeError:
        return abort(406, "EndTime must be greater than StartTime and StartTime must be greater than CreationTime")


@app.api_route('<string:cid>/', methods=['DELETE'])
@auth.authenticate
def delete(cid):
    """
    Contest Delete
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
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
        description: You aren't owner of the contest
      404:
        description: Contest does not exist
    """

    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)

        if user_obj != obj.owner:
            return abort(403, "You aren't owner of the contest")

        obj.delete()
        return '', 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


@app.api_route('', methods=['GET'])
@paginate('contests', 20)
@auth.authenticate
def list():
    """
    Get All Contests List
    ---
    tags:
      - contest
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        description: Page number
      - name: per_page
        in: query
        type: integer
        required: false
        description: Contest amount per page (default is 10)
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: List of contests
        schema:
          id: ContestsListUser
          type: object
          properties:
            contests:
              type: array
              items:
                $ref: "#/definitions/api_1_contest_info_get_ContestInfoUser"
            meta:
              type: object
              description: Pagination meta data
              properties:
                first:
                  type: string
                  description: Url for first page of results
                last:
                  type: string
                  description: Url for last page of results
                next:
                  type: string
                  description: Url for next page of results
                prev:
                  type: string
                  description: Url for previous page of results
                page:
                  type: integer
                  description: Number of the current page
                pages:
                  type: integer
                  description: All pages count
                per_page:
                  type: integer
                  description: Item per each page
                total:
                  type: integer
                  description: Total count of all items
      401:
        description: Token is invalid or has expired
    """

    user_obj = User.objects.get(pk=g.user_id)
    contests = Contest.objects.order_by('-starts_at')
    result_func = lambda obj: Contest.to_json_user(obj, user_obj)
    return contests, result_func


@app.api_route('owner', methods=['GET'])
@paginate('contests', 20)
@auth.authenticate
def list_owner():
    """
    Get Owner Contests
    ---
    tags:
      - contest
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        description: Page number
      - name: per_page
        in: query
        type: integer
        required: false
        description: Contest amount per page (default is 10)
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: List of contests
        schema:
          id: ContestsList
          type: object
          properties:
            contests:
              type: array
              items:
                schema:
                  id: ContestInfo
                  type: object
                  properties:
                    id:
                      type: string
                      description: Contest id
                    name:
                      type: string
                      description: Contest name
                    owner:
                      description: Owner info
                      schema:
                          id: ContestOwnerInfo
                          type: object
                          properties:
                            id:
                              type: string
                              description: Owner id
                            username:
                              type: string
                              description: Owner username
                    created_at:
                      type: integer
                      description: Contest created_at (utc timestamp)
                    starts_at:
                      type: integer
                      description: Contest starts_at (utc timestamp)
                    ends_at:
                      type: integer
                      description: Contest ends_at (utc timestamp)
                    is_active:
                      type: boolean
                      description: Contest is_active
                    is_ended:
                      type: boolean
                      description: Contest is_ended
                    pending_teams_num:
                      type: integer
                      description: Contest number of pending teams
                    accepted_teams_num:
                      type: integer
                      description: Contest number of accepted teams
      401:
        description: Token is invalid or has expired
    """

    user_obj = User.objects.get(pk=g.user_id)
    contests = Contest.objects.filter(owner=user_obj).order_by('-starts_at')
    result_func = lambda obj: Contest.to_json(obj)
    return contests, result_func


@app.api_route('<string:cid>/result', methods=['GET'])
@auth.authenticate
def result(cid):
    """
    Get Result
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Result information
        schema:
          id: ContestResult
          type: object
          properties:
            result:
              type: object
              properties:
                team_id*:
                  type: object
                  description: Teams result dictionary (team_id => team_data). 
                               Teams without submission aren't in this dictionary
                  properties:
                    penalty:
                      type: integer
                    solved_count:
                      type: integer
                    problems:
                      type: object
                      properties:
                        problem_id*:
                          type: object
                          description: Problems result dictionary (problem_id => problem_data). 
                                       Problems without submission aren't in this dictionary
                          properties:
                            submitted_at:
                              type: integer
                              description: Last submission time (utc timestmap) (default=null)
                            failed_tries:
                              type: integer
                            penalty:
                              type: integer
                            solved:
                              type: boolean
            teams:
              type: array
              description: Teams list (sorted by rank in contest)
              items:
                schema:
                  properties:
                    id:
                      type: string
                      description: Team id
                    name:
                      type: string
                      description: Team name
            problems:
              type: array
              description: Problems list
              items:
                schema:
                  properties:
                    id:
                      type: string
                      description: Problem id
                    title:
                      type: string
                      description: Problem title
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't allowed to see result
      404:
        description: Contest does not exist
    """

    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)
        now = utcnowts()

        if not (user_obj == obj.owner or user_obj in obj.admins or \
               (now >= obj.starts_at and obj.is_user_in_contest(user_obj)) or \
               (now > obj.ends_at)):
            return abort(403, "You aren't allowed to see result")

        return jsonify(obj.to_json_result()), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


################################# Team #################################


@app.api_route('team/<string:tid>', methods=['GET'])
@auth.authenticate
def list_team(tid):
    """
    Get Contests List of a Team
    ---
    tags:
      - contest
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
        description: Team contests list
        schema:
          id: TeamContestsList
          type: object
          properties:
            waiting_contests:
              type: array
              items:
                schema:
                  $ref: "#/definitions/api_1_contest_list_owner_get_ContestInfo"
            joined_contests:
              type: array
              items:
                schema:
                  $ref: "#/definitions/api_1_contest_list_owner_get_ContestInfo"
      401:
        description: Token is invalid or has expired
      404:
        description: Team does not exist
    """

    try:
        obj = Team.objects.get(pk=tid)
        wc = Contest.objects.filter(pending_teams=obj)
        wc = [c.to_json() for c in wc]
        jc = Contest.objects.filter(accepted_teams=obj)
        jc = [c.to_json() for c in jc]

        return jsonify(waiting_contests=wc, joined_contests=jc), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Team does not exist")


@app.api_route('<string:cid>/team', methods=['POST'])
@app.api_validate('contest.team_join_schema')
@auth.authenticate
def team_join(cid):
    """
    Team Join
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: body
        in: body
        description: Team Identification
        required: true
        schema:
          id: TeamIdentification
          properties:
            team_id:
              type: string
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Join request sent
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner of the team
      404:
        description: Contest or Team does not exist
      409:
        description: You are already accepted
    """

    json = request.json
    try:
        obj = Contest.objects.get(pk=cid)
        team_obj = Team.objects.get(pk=json['team_id'])

        if str(team_obj.owner.pk) != g.user_id:
            return abort(403, "You aren't owner of the team")

        if team_obj in obj.accepted_teams:
            return abort(409, "You are already accepted")

        obj.update(add_to_set__pending_teams=team_obj)
        return '', 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or Team does not exist")


@app.api_route('<string:cid>/team/<string:tid>', methods=['DELETE'])
@auth.authenticate
def team_unjoin(cid, tid):
    """
    Team Unjoin
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
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
        description: Successfully unjoined
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner of the team
      404:
        description: Contest or Team does not exist
    """

    try:
        team_obj = Team.objects.get(pk=tid)
        obj = Contest.objects.get(pk=cid, pending_teams=team_obj)

        if str(team_obj.owner.pk) != g.user_id:
            return abort(403, "You aren't owner of the team")

        obj.update(pull__pending_teams=team_obj)
        return '', 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or Team does not exist")


@app.api_route('<string:cid>/pending_teams', methods=['GET'])
@auth.authenticate
def team_list_pending(cid):
    """
    Team Get Pending List
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: List of pending teams
        schema:
          id: ContestTeamsList
          type: object
          properties:
            teams:
              type: array
              items:
                schema:
                  $ref: "#/definitions/api_1_team_info_get_TeamInfo"
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest does not exist
    """

    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        return jsonify(obj.to_json_teams('pending')), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


@app.api_route('<string:cid>/accepted_teams', methods=['GET'])
@auth.authenticate
def team_list_accepted(cid):
    """
    Team Get Accepted List
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: List of accepted teams
        schema:
          $ref: "#/definitions/api_1_contest_team_list_pending_get_ContestTeamsList"
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest does not exist
    """

    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        return jsonify(obj.to_json_teams('accepted')), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


@app.api_route('<string:cid>/team/<string:tid>/acceptation', methods=['PATCH'])
@auth.authenticate
def team_accept(cid, tid):
    """
    Team Accept
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
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
        description: Successfully accepted
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest or Team does not exist
    """

    try:
        team_obj = Team.objects.get(pk=tid)
        obj = Contest.objects.get(pk=cid, pending_teams=team_obj)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        obj.update(pull__pending_teams=team_obj, add_to_set__accepted_teams=team_obj)
        return '', 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or Team does not exist")


@app.api_route('<string:cid>/team/<string:tid>/acceptation', methods=['DELETE'])
@auth.authenticate
def team_reject(cid, tid):
    """
    Team Reject
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
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
        description: Successfully rejected
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest or Team does not exist
    """

    try:
        team_obj = Team.objects.get(pk=tid)
        obj = Contest.objects.get(pk=cid, pending_teams=team_obj)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        obj.update(pull__pending_teams=team_obj)
        return '', 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or Team does not exist")


@app.api_route('<string:cid>/team/<string:tid>/kick', methods=['DELETE'])
@auth.authenticate
def team_kick(cid, tid):
    """
    Team Kick
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
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
        description: Successfully kicked
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest or Team does not exist
    """

    try:
        team_obj = Team.objects.get(pk=tid)
        obj = Contest.objects.get(pk=cid, accepted_teams=team_obj)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        obj.update(pull__accepted_teams=team_obj)
        return '', 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or Team does not exist")


################################# Problem #################################


@app.api_route('<string:cid>/problem', methods=['POST'])
@app.api_validate('contest.problem_create_schema')
@auth.authenticate
def problem_create(cid):
    """
    Problem Create
    Maximum number of problems can be created is 20
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: body
        in: body
        description: Problem information
        required: true
        schema:
          id: ProblemCreation
          required:
            - title
            - time_limit
            - space_limit
          properties:
            title:
              type: string
              example: babyknight
              minLength: 1
              maxLength: 32
            time_limit:
              type: number
              minimum: 0.1
              maximum: 10
              description: Problem time limit (seconds)
            space_limit:
              type: integer
              minimum: 16
              maximum: 256
              description: Problem space limit (mega bytes)
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      201:
        description: Successfully created
        schema:
          $ref: "#/definitions/api_1_contest_problem_info_get_ProblemInfo"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest does not exist
      406:
        description: You can't create more problems
    """

    json = request.json
    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        if len(obj.problems) >= 20:
            return abort(406, "You can't create more problems")

        problem_obj = Problem()
        problem_obj.populate(json)
        problem_obj.save()
        obj.update(push__problems=problem_obj)
        return jsonify(problem_obj.to_json()), 201

    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


@app.api_route('<string:cid>/problem/<string:pid>', methods=['GET'])
@auth.authenticate
def problem_info(cid, pid):
    """
    Problem Get Info
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: pid
        in: path
        type: string
        required: true
        description: Id of problem
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Problem information
        schema:
          id: ProblemInfo
          type: object
          properties:
            id:
              type: string
              description: Problem id
            title:
              type: string
              description: Problem title
            time_limit:
              type: number
              description: Problem time limit (seconds)
            space_limit:
              type: integer
              description: Problem space limit (mega bytes)
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't allowed to see problem
      404:
        description: Contest or problem does not exist
    """

    try:
        problem_obj = Problem.objects.get(pk=pid)
        obj = Contest.objects.get(pk=cid, problems=problem_obj)
        user_obj = User.objects.get(pk=g.user_id)
        now = utcnowts()

        if not (user_obj == obj.owner or user_obj in obj.admins or \
               (now >= obj.starts_at and obj.is_user_in_contest(user_obj)) or \
               (now > obj.ends_at)):
            return abort(403, "You aren't allowed to see problem")

        return jsonify(problem_obj.to_json()), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or problem does not exist")


@app.api_route('<string:cid>/problem', methods=['GET'])
@auth.authenticate
def problem_list(cid):
    """
    Problem Get List
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: List of problems
        schema:
          id: ContestProblemsList
          type: object
          properties:
            problems:
              type: array
              items:
                schema:
                  id: ProblemAbsInfo
                  type: object
                  properties:
                    id:
                      type: string
                      description: Problem id
                    title:
                      type: string
                      description: Problem title
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't allowed to see problems
      404:
        description: Contest does not exist
    """

    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)
        now = utcnowts()

        if not (user_obj == obj.owner or user_obj in obj.admins or \
               (now >= obj.starts_at and obj.is_user_in_contest(user_obj)) or \
               (now > obj.ends_at)):
            return abort(403, "You aren't allowed to see problems")

        return jsonify(obj.to_json_problems()), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


@app.api_route('<string:cid>/problem/<string:pid>', methods=['PUT'])
@app.api_validate('contest.problem_edit_schema')
@auth.authenticate
def problem_edit(cid, pid):
    """
    Problem Edit
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: pid
        in: path
        type: string
        required: true
        description: Id of problem
      - name: body
        in: body
        description: Problem information
        required: true
        schema:
          id: ProblemEdition
          properties:
            title:
              type: string
              example: babyknight
              minLength: 1
              maxLength: 32
            time_limit:
              type: number
              minimum: 0.1
              maximum: 10
              description: Problem time limit (seconds)
            space_limit:
              type: integer
              minimum: 16
              maximum: 256
              description: Problem space limit (mega bytes)
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully edited
        schema:
          $ref: "#/definitions/api_1_contest_problem_info_get_ProblemInfo"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest or problem does not exist
    """

    json = request.json
    try:
        problem_obj = Problem.objects.get(pk=pid)
        obj = Contest.objects.get(pk=cid, problems=problem_obj)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        problem_obj.populate(json)
        problem_obj.save()
        return jsonify(problem_obj.to_json()), 200

    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or problem does not exist")


@app.api_route('<string:cid>/problem', methods=['PATCH'])
@app.api_validate('contest.problem_change_order_schema')
@auth.authenticate
def problem_change_order(cid):
    """
    Problem Change Order
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: body
        in: body
        description: Problems order
        required: true
        schema:
          id: ProblemsOrder
          required:
          - order
          properties:
            order:
              type: array
              items:
                type: integer
                description: order number
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: List of problems
        schema:
          $ref: "#/definitions/api_1_contest_problem_list_get_ContestProblemsList"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest does not exist
      406:
        description: Bad order format
    """

    json = request.json
    try:
        obj = Contest.objects.get(pk=cid)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        if len(list(set(json['order']))) != len(json['order']) or \
            len(json['order']) != len(obj.problems):
            return abort(406, "Bad order format")

        new_problems = []
        for i in json['order']:
            new_problems.append(obj.problems[i])
        obj.problems = new_problems
        obj.save()

        return jsonify(obj.to_json_problems()), 200
    except IndexError:
        return abort(406, "Bad order format")
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


@app.api_route('<string:cid>/problem/<string:pid>', methods=['DELETE'])
@auth.authenticate
def problem_delete(cid, pid):
    """
    Problem Delete
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: pid
        in: path
        type: string
        required: true
        description: Id of problem
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully deleted
        schema:
          $ref: "#/definitions/api_1_contest_problem_list_get_ContestProblemsList"
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest or problem does not exist
    """

    try:
        problem_obj = Problem.objects.get(pk=pid)
        obj = Contest.objects.get(pk=cid, problems=problem_obj)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        problem_obj.delete()
        obj.reload()
        return jsonify(obj.to_json_problems()), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or problem does not exist")


@app.api_route('<string:cid>/problem/<string:pid>/body', methods=['POST'])
@auth.authenticate
def problem_upload_body(cid, pid):
    """
    Problem Upload Body File
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: pid
        in: path
        type: string
        required: true
        description: Id of problem
      - name: body
        in: formData
        type: file
        required: true
        description: Problem body file (pdf) (max size is 16M)
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully uploaded
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest or problem does not exist
      413:
        description: Request entity too large. (max size is 16M)
      415:
        description: Supported file type is only application/pdf
    """

    try:
        problem_obj = Problem.objects.get(pk=pid)
        obj = Contest.objects.get(pk=cid, problems=problem_obj)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        form = UploadProblemBody()
        if not form.validate():
            return abort(400, "Bad request")

        if not form.validate_file():
            return abort(415, "Supported file type is only application/pdf")

        file_obj = form.body.data
        file_obj.save(problem_obj.body_path)

        return "", 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or problem does not exist")


@app.api_route('<string:cid>/problem/<string:pid>/testcase', methods=['POST'])
@auth.authenticate
def problem_upload_testcase(cid, pid):
    """
    Problem Upload Testcase File
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: pid
        in: path
        type: string
        required: true
        description: Id of problem
      - name: testcase
        in: formData
        type: file
        required: true
        description: Problem testcase file (zip) (max size is 16M)
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully uploaded
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner or admin of the contest
      404:
        description: Contest or problem does not exist
      413:
        description: Request entity too large. (max size is 16M)
      415:
        description: Supported file type is only application/zip
    """

    try:
        problem_obj = Problem.objects.get(pk=pid)
        obj = Contest.objects.get(pk=cid, problems=problem_obj)
        user_obj = User.objects.get(pk=g.user_id)

        if (user_obj != obj.owner) and (not user_obj in obj.admins):
            return abort(403, "You aren't owner or admin of the contest")

        form = UploadTestCase()
        if not form.validate():
            return abort(400, "Bad request")

        if not form.validate_file():
            return abort(415, "Supported file type is only application/zip")

        if os.path.exists(problem_obj.testcase_dir):
            shutil.rmtree(problem_obj.testcase_dir)

        file_obj = form.testcase.data
        with zipfile.ZipFile(file_obj) as zf:
            zf.extractall(problem_obj.testcase_dir)

        return "", 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or problem does not exist")


@app.api_route('<string:cid>/problem/<string:pid>/body', methods=['GET'])
@auth.authenticate
def problem_download_body(cid, pid):
    """
    Problem Download Body File
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: pid
        in: path
        type: string
        required: true
        description: Id of problem
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Problem body file
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't allowed to see problem body
      404:
        description: (Contest or problem does not exist, File does not exist)
    """

    try:
        problem_obj = Problem.objects.get(pk=pid)
        obj = Contest.objects.get(pk=cid, problems=problem_obj)
        user_obj = User.objects.get(pk=g.user_id)
        now = utcnowts()

        if not (user_obj == obj.owner or user_obj in obj.admins or \
               (now >= obj.starts_at and obj.is_user_in_contest(user_obj)) or \
               (now > obj.ends_at)):
            return abort(403, "You aren't allowed to see problem body")

        data = open(problem_obj.body_path).read()
        data = base64.b64encode(data)
        data_io = StringIO.StringIO(data)
        return send_file(data_io, mimetype='application/pdf')
    except IOError:
        return abort(404, "File does not exist")
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or problem does not exist")


################################# Admin #################################


@app.api_route('<string:cid>/admin', methods=['POST'])
@app.api_validate('contest.admin_add_schema')
@auth.authenticate
def admin_add(cid):
    """
    Admin Add
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: body
        in: body
        description: Problem information
        required: true
        schema:
          id: AdminIdentificationName
          required:
            - username
          properties:
            username:
              type: string
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      201:
        description: Admin added
        schema:
          $ref: "#/definitions/api_1_contest_admin_list_get_AdminsList"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner of the contest
      404:
        description: Contest or user does not exist
    """

    json = request.json
    try:
        obj = Contest.objects.get(pk=cid)
        if str(obj.owner.pk) != g.user_id:
            return abort(403, "You aren't owner of the contest")

        user_obj = User.objects.get(username=json['username'])
        if user_obj != obj.owner:
            obj.update(add_to_set__admins=user_obj)
        obj.reload()

        return jsonify(obj.to_json_admins()), 201
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or user does not exist")


@app.api_route('<string:cid>/admin/<string:uid>', methods=['DELETE'])
@auth.authenticate
def admin_remove(cid, uid):
    """
    Admin Remove
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: uid
        in: path
        type: string
        required: true
        description: Id of user
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successully removed
        schema:
          $ref: "#/definitions/api_1_contest_admin_list_get_AdminsList"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner of the contest
      404:
        description: Contest or user does not exist
    """

    try:
        obj = Contest.objects.get(pk=cid)
        if str(obj.owner.pk) != g.user_id:
            return abort(403, "You aren't owner of the contest")

        user_obj = User.objects.get(pk=uid)

        obj.update(pull__admins=user_obj)
        obj.reload()
        return jsonify(obj.to_json_admins()), 200

    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest or user does not exist")


@app.api_route('<string:cid>/admin', methods=['GET'])
@auth.authenticate
def admin_list(cid):
    """
    Admin List
    ---
    tags:
      - contest
    parameters:
      - name: cid
        in: path
        type: string
        required: true
        description: Id of contest
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: List of admins
        schema:
          id: AdminsList
          properties:
            admins:
              type: array
              items:
                schema:
                  $ref: "#/definitions/api_1_team_info_get_UserAbsInfo"
      401:
        description: Token is invalid or has expired
      403:
        description: You aren't owner of the contest
      404:
        description: Contest does not exist
    """

    try:
        obj = Contest.objects.get(pk=cid)
        if str(obj.owner.pk) != g.user_id:
            return abort(403, "You aren't owner of the contest")

        return jsonify(obj.to_json_admins()), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "Contest does not exist")


@app.api_route('admin', methods=['GET'])
@paginate('contests', 20)
@auth.authenticate
def admin_contests():
    """
    Get Admin Contests
    ---
    tags:
      - contest
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        description: Page number
      - name: per_page
        in: query
        type: integer
        required: false
        description: Contest amount per page (default is 10)
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: List of contests
        schema:
          $ref: "#/definitions/api_1_contest_list_owner_get_ContestsList"
      401:
        description: Token is invalid or has expired
    """

    user_obj = User.objects.get(pk=g.user_id)
    contests = Contest.objects.filter(admins=user_obj).order_by('-starts_at')
    result_func = lambda obj: Contest.to_json(obj)
    return contests, result_func
