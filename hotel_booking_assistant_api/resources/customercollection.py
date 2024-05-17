"""
Resource methods for CustomerCollection
"""
import json
from flask_restful import Resource
from flask import Response, request
from werkzeug.exceptions import HTTPException
from jsonschema import validate, ValidationError, draft7_format_checker
from sqlalchemy import exc
from orm import Customer, db, BookingAssistantBuilder, create_error_response
from keyFunc import any_admin
from static.constants import MASON, LINK_RELATIONS_URL

class CustomerCollection(Resource):

    """ Class with method for adding new entries to Customer table """

    @any_admin
    def post(self):

        """ Create new Customer entry (POST) """

        # check request type
        if request.headers["Content-Type"] != "application/json":
            raise HTTPException(response=create_error_response(
                415,
                "UnsupportedMediaType",
                "Request type was not JSON!"))

        # validate request format
        try:
            validate(request.json, Customer.json_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise HTTPException(response=create_error_response(400,
                "BadRequest", str(e))) from e

        try:
            # add new customer entry
            customer_entry = Customer(
                name=request.json["name"], phone=request.json["phone"],
                mail=request.json["mail"], address=request.json["address"]
                )

            # add customer entry to database
            db.session.add(customer_entry)
            db.session.commit()

        except exc.IntegrityError:
            return create_error_response(409,
                "Conflict",
                "Failure in POST: E-mail already in use")

        # generate hypermedia response
        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control_get_customer(customer_entry)
        body["item"] = [customer_entry.serialize(short_form=True)]

        # return success response
        return Response(json.dumps(body), status=201, mimetype=MASON)
