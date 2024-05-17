"""
Resource methods for CustomerItem
"""
import json
from jsonschema import validate, ValidationError, draft7_format_checker
from werkzeug.exceptions import HTTPException
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy import exc
from orm import Booking, Customer, db, BookingAssistantBuilder, create_error_response
from keyFunc import any_admin
from static.constants import MASON, LINK_RELATIONS_URL

class CustomerItem(Resource):

    """ Class with methods for getting, deleting and modifying Customer information """

    # get customer
    @any_admin
    def get(self, customer):

        """ Get Customer entry (GET) """

        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control("self", href=url_for("customer", customer=customer))
        body.add_control("collection", href=url_for("customercollection"))
        body.add_control_edit_customer(customer)
        body.add_control_delete_customer(customer)
        body.add_control_add_bookings()
        body.add_control_avl_rooms()
        body["item"] = [customer.serialize(short_form=True)]

        return Response(json.dumps(body), status=200, mimetype = MASON)

    # delete customer
    @any_admin
    def delete(self, customer):

        """ Delete existing Customer entry (DELETE) """

        # get bookings for customer
        booking = Booking.query.filter_by(customer_id=customer.id).first()

        # if customer has any bookings, DELETE is not allowed
        if booking:
            return create_error_response(405,
                "Method Not Allowed",
                "DELETE not permitted (Customer has bookings)")

        # delete customer
        db.session.delete(customer)
        db.session.commit()
        return Response(status=204, mimetype = MASON)

    # modify customer
    @any_admin
    def put(self, customer):

        """ Modify existing Customer entry (PUT) """

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
            # update customer entry
            customer.name = request.json["name"]
            customer.mail = request.json["mail"]
            customer.phone = request.json["phone"]
            customer.address = request.json["address"]
            db.session.commit()
        except exc.IntegrityError:
            return create_error_response(409, "Conflict", "Failure in PUT: E-mail already in use")

        # return success response
        return Response(status=204, mimetype=MASON)
