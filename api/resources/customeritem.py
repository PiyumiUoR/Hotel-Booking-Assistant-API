import json
from jsonschema import validate, ValidationError, draft7_format_checker
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from orm import Booking, Customer, db, BookingAssistantBuilder
from keyFunc import customer_admin, any_admin
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy import exc
from static.constants import MASON, LINK_RELATIONS_URL, CUSTOMER_PROFILE_URL

class CustomerItem(Resource):

    """ Class with methods for getting, deleting and modifying Customer information """

    @customer_admin
    def get(self, customer):

        """ Get Customer entry (GET) """

        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        # body.add_control("self", href = CUSTOMER_PROFILE_URL)
        body.add_control_get_customer(customer)
        body.add_control_add_customer()
        body.add_control_edit_customer(customer)
        body.add_control_delete_customer(customer)
        
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
            return "DELETE not permitted (Customer has bookings)", 405
        
        # delete customer
        db.session.delete(customer)
        db.session.commit()

        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)        
        body.add_control_add_customer()
        # return response
        return Response(json.dumps(body), status=200, mimetype = MASON)

    # modify customer
    @customer_admin
    def put(self, customer):

        """ Modify existing Customer entry (PUT) """

        # check request type
        if request.headers["Content-Type"] != "application/json":
            raise UnsupportedMediaType
        
        # validate request format
        try:
            validate(request.json, Customer.json_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e
        
        try:
            # update customer entry
            customer.name = request.json["name"]
            customer.mail = request.json["mail"]
            customer.phone = request.json["phone"]
            customer.address = request.json["address"]
            db.session.commit()
        except exc.IntegrityError:
            return "Failure in PUT: E-mail already in use", 409
        
        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control_get_customer(customer)
        body.add_control_add_customer()
        body.add_control_edit_customer(customer)
        body.add_control_delete_customer(customer)
        
        body["item"] = [customer.serialize(short_form=True)]

        return Response(json.dumps(body), status=200, mimetype = MASON)