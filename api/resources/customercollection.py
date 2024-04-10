import json
from flask_restful import Resource
from flask import Response, request, url_for
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from jsonschema import validate, ValidationError, draft7_format_checker
from sqlalchemy import exc
from orm import Customer, db, BookingAssistantBuilder
from keyFunc import any_admin
from static.constants import MASON, LINK_RELATIONS_URL

class CustomerCollection(Resource):

    """ Class with method for adding new entries to Customer table """

    @any_admin
    def post(self):

        """ Create new Customer entry (POST) """

        # check request type
        if request.headers["Content-Type"] != "application/json":
            raise UnsupportedMediaType

        # validate request format
        try:
            validate(request.json, Customer.json_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

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
            return "Failure in POST: E-mail already in use", 409
        
        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        # body.add_control("self", href = CUSTOMER_PROFILE_URL)
        body.add_control_get_customer(customer_entry)
        body.add_control_add_customer()
        body.add_control_edit_customer(customer_entry)
        body.add_control_delete_customer(customer_entry)
        
        body["item"] = [customer_entry.serialize(short_form=True)]
        
        # return success response
        return Response(json.dumps(body), status=200, mimetype = MASON)