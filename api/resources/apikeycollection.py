import secrets
import json
from flask_restful import Resource
from flask import Response, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from jsonschema import validate, ValidationError, draft7_format_checker
from orm import Admin, ApiKey, db, BookingAssistantBuilder
from keyFunc import any_admin
from static.constants import MASON, LINK_RELATIONS_URL

class ApiKeyCollection(Resource):

    """ Class with methods for deleting and adding new entries to ApiKey table """

    @any_admin
    def delete(self):

        """ Delete existing ApiKey entry (DELETE) """

        # get apikey of admin
        apikey = ApiKey.query.filter_by(admin_username=request.headers["Admin-User-Name"]).first()

        # delete customer
        db.session.delete(apikey)

        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control_add_apikey()

        db.session.commit()

        # return response
        return Response(json.dumps(body), status=200, mimetype = MASON)

    def post(self):

        """ Create new ApiKey entry (POST) """

        # check request type
        if request.headers["Content-Type"] != "application/json":
            raise UnsupportedMediaType

        # validate request format
        try:
            validate(request.json, ApiKey.json_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        # get admin
        admin = Admin.query.filter_by(
            username=request.json["username"],
            password=request.json["password"]).first()

        # check if admin was found
        if admin is None:
            return "Incorrect username or password!", 401

        # generate plain text token
        token = secrets.token_urlsafe()

        # check if admin already has an API key
        apikey = ApiKey.query.filter_by(admin_username=admin.username).first()
        if apikey is not None:
            return "Failure in POST: Admin already has an API key!", 409

        # create apikey entry
        apikey_entry = ApiKey(key=ApiKey.key_hash(token), admin=admin)

        #create apikey entry for the MasonBuilder output
        apikey_entry_mb = ApiKey(key=token, admin=admin)

        # add apikey to database
        db.session.add(apikey_entry)
        db.session.commit()

        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control_delete_apikey(apikey_entry)

        body["item"] = [apikey_entry_mb.serialize(short_form=True)]

        # return success response
        # return Response(status=201, headers={"Hotels-Api-Key": token})
        return Response(json.dumps(body), status=200, mimetype = MASON)


