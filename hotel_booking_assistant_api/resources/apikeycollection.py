"""
Resource methods for ApiKeyCollection
"""

import secrets
from flask_restful import Resource
from flask import Response, request
from werkzeug.exceptions import HTTPException
from jsonschema import validate, ValidationError, draft7_format_checker
from orm import Admin, ApiKey, db, create_error_response
from keyFunc import any_admin
from static.constants import MASON

class ApiKeyCollection(Resource):

    """ Class with methods for deleting and adding new entries to ApiKey table """

    @any_admin
    def delete(self):

        """ Delete existing ApiKey entry (DELETE) """

        # get apikey of admin
        apikey = ApiKey.query.filter_by(admin_username=request.headers["Admin-User-Name"]).first()

        # delete apikey of admin
        db.session.delete(apikey)
        db.session.commit()

        # return response
        return Response(status=204, mimetype=MASON)

    def post(self):

        """ Create new ApiKey entry (POST) """

        # check request type
        if request.headers["Content-Type"] != "application/json":
            raise HTTPException(response=create_error_response(
                415,
                "UnsupportedMediaType",
                "Request type was not JSON!")
                )

        # validate request format
        try:
            validate(request.json, ApiKey.json_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise HTTPException(response=create_error_response(400, "BadRequest", str(e))) from e

        # get admin
        admin = Admin.query.filter_by(
            username=request.json["username"],
            password=request.json["password"]).first()

        # check if admin was found
        if admin is None:
            return create_error_response(401,
                "Unauthorized",
                "Incorrect username or password!"
                )

        # generate plain text token
        token = secrets.token_urlsafe()

        # check if admin already has an API key
        apikey = ApiKey.query.filter_by(admin_username=admin.username).first()
        if apikey is not None:
            return create_error_response(
                409,
                "Conflict",
                "Failure in POST: Admin already has an API key!"
                )

        # create apikey entry
        apikey_entry = ApiKey(key=ApiKey.key_hash(token), admin=admin)

        # add apikey to database
        db.session.add(apikey_entry)
        db.session.commit()

        # return success response
        return Response(status=201, headers={"Hotels-Api-Key": token}, mimetype=MASON)
