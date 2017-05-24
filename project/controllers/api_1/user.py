# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# flask imports
from flask import jsonify, request, g, abort

# project imports
from project import app
from project.extensions import db, auth
from project.models.user import User


@app.api_route('signup', methods=['POST'])
@app.api_validate('user.signup_schema')
def signup():
    """
    Signup
    ---
    tags:
      - user
    parameters:
      - name: body
        in: body
        description: username, email and password for signup
        required: true
        schema:
          id: UserSignup
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              pattern: ^[a-zA-Z0-9_]*$
              example: babyknight
              minLength: 1
              maxLength: 32
            email:
              type: string
              example: baby@knight.org
            password:
              type: string
              example: baby123
              minLength: 3
              maxLength: 32
            recaptcha:
              type: string
    responses:
      201:
        description: Successfully registered
        schema:
          $ref: "#/definitions/api_1_user_info_get_UserInfo"
      400:
        description: Bad request
      409:
        description: Email or username already exists
    """

    json = request.json
    try:
        obj = User()
        obj.populate(json)
        obj.hash_password(json['password'])
        obj.save()
        return jsonify(obj.to_json()), 201
    except db.NotUniqueError:
        return abort(409, "Email or username already exists")


@app.api_route('login', methods=['POST'])
@app.api_validate('user.login_schema')
def login():
    """
    Login
    ---
    tags:
      - user
    parameters:
      - name: body
        in: body
        description: username/email and password for login
        required: true
        schema:
          id: UserLogin
          required:
            - login
            - password
          properties:
            login:
              type: string
              example: babyknight
              description: Username or Email
            password:
              type: string
              example: baby123
    responses:
      200:
        description: Successfully logged in
        schema:
          type: object
          properties:
            token:
              type: string
              description: Generated RESTful token
      400:
        description: Bad request
      404:
        description: User does not exist
      406:
        description: Wrong password
    """

    json = request.json
    login = json['login']
    password = json['password']

    try:
        if '@' in login:
            obj = User.objects.get(email=login)
        else:
            obj = User.objects.get(username=login)

        if obj.verify_password(password):
            token = auth.generate_token(obj.pk)
            return jsonify(token=token), 200
        else:
            return abort(406, "Wrong password")

    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "User does not exist")


@app.api_route('login_with_token', methods=['POST'])
@auth.authenticate
def login_with_token():
    """
    Login with Token
    ---
    tags:
      - user
    parameters:
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully logged in
      401:
        description: Token is invalid or has expired
    """

    return '', 200


@app.api_route('logout', methods=['POST'])
@auth.authenticate
def logout():
    """
    Logout
    ---
    tags:
      - user
    parameters:
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully logged out
      401:
        description: Token is invalid or has expired
    """

    auth.expire_token()
    return '', 200


@app.api_route('<string:uid>', methods=['GET'])
@auth.authenticate
def info(uid):
    """
    Get User Info
    ---
    tags:
      - user
    parameters:
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
        description: User information
        schema:
          id: UserInfo
          type: object
          properties:
            id:
              type: string
              description: User id
            username:
              type: string
              description: Username
            email:
              type: string
              description: Email
            firstname:
              type: string
              description: First name
            lastname:
              type: string
              description: Last name
      401:
        description: Token is invalid or has expired
      404:
        description: User does not exist
    """

    try:
        obj = User.objects.get(pk=uid)
        return jsonify(obj.to_json()), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "User does not exist")


@app.api_route('', methods=['GET'])
@auth.authenticate
def myinfo():
    """
    Get Current User Info
    ---
    tags:
      - user
    parameters:
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Currnt user information
        schema:
          $ref: "#/definitions/api_1_user_info_get_UserInfo"
      401:
        description: Token is invalid or has expired
      404:
        description: User does not exist
    """

    return info(uid=g.user_id)


@app.api_route('', methods=['PUT'])
@app.api_validate('user.edit_schema')
@auth.authenticate
def edit():
    """
    Edit
    ---
    tags:
      - user
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: UserEdit
          properties:
            email:
              type: string
              example: new_baby@knight.org
            password:
              schema:
                properties:
                  old_password:
                    type: string
                    example: baby123
                    minLength: 3
                    maxLength: 32
                  new_password:
                    type: string
                    example: baby123
                    minLength: 3
                    maxLength: 32
            firstname:
              type: string
              minLength: 1
              maxLength: 32
            lastname:
              type: string
              minLength: 1
              maxLength: 32
      - name: Access-Token
        in: header
        type: string
        required: true
        description: Token of current user
    responses:
      200:
        description: Successfully edited
        schema:
          $ref: "#/definitions/api_1_user_info_get_UserInfo"
      400:
        description: Bad request
      401:
        description: Token is invalid or has expired
      404:
        description: User does not exist
      406:
        description: Wrong password
    """

    json = request.json
    try:
        obj = User.objects.get(pk=g.user_id)
        obj.populate(json)
        if 'password' in json:
            old_password = json['password']['old_password']
            new_password = json['password']['new_password']
            if not obj.change_password(old_password, new_password):
                return abort(406, "Wrong password")
        obj.save()
        return jsonify(obj.to_json()), 200
    except (db.DoesNotExist, db.ValidationError):
        return abort(404, "User does not exist")
