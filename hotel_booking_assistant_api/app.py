""" Main file for Hotel-Booking-Assistant API """

# IMPORTS
import json
from werkzeug.exceptions import HTTPException
from werkzeug.routing import BaseConverter
from flask_restful import Api
from flask import Response, request, send_from_directory
from orm import Booking, Customer, app, BookingAssistantBuilder, create_error_response
from static.constants import LINK_RELATIONS_URL, MASON
from resources.apikeycollection import ApiKeyCollection
from resources.roomcollection import RoomCollection
from resources.customeritem import CustomerItem
from resources.customercollection import CustomerCollection
from resources.bookingitem import BookingItem
from resources.bookingcollection import BookingCollection

api = Api(app)

class CustomerConverter(BaseConverter):
    """
    Base converter for Customer
    """
    def to_python(self, value):
        customer_db = Customer.query.filter_by(id=value).first()
        if customer_db is None:
            # allow 405 to be raised (no double exceptions)
            if request.method != "POST":
                raise HTTPException(
                    response=create_error_response(
                        404,
                        "NotFound",
                        f'Customer with id: {value} was not found!')
                    )
        return customer_db

    def to_url(self, value):
        return str(value.id)

class BookingConverter(BaseConverter):
    """
    Base converter for Booking
    """
    def to_python(self, value):
        booking_db = Booking.query.filter_by(booking_ref=value).first()
        if booking_db is None:
            # allow 405 to be raised (no double exceptions)
            if request.method != "POST":
                raise HTTPException(
                    response=create_error_response(
                        404,
                        "NotFound",
                        f'Booking with id: {value} was not found!')
                    )
        return booking_db

    def to_url(self, value):
        return str(value.booking_ref)

@app.route("/api/")
def entry_point():
    """
    Entry point to API
    """
    body = BookingAssistantBuilder()
    body["@namespace"] = {
        "bookie": {
            "name": LINK_RELATIONS_URL
        }
    }

    body.add_control_add_bookings()
    body.add_control_add_customer()
    body.add_control_add_apikey()
    body.add_control_delete_apikey()
    return Response(json.dumps(body), mimetype=MASON, status=200)

@app.route(LINK_RELATIONS_URL)
def send_link_relations_html():
    """
    Get link relation document (HTML)
    """
    return send_from_directory(app.static_folder, "links-relations.html")

# add converters
app.url_map.converters["customer"] = CustomerConverter
app.url_map.converters["booking"] = BookingConverter

# add resources
api.add_resource(ApiKeyCollection, "/api/keys/", endpoint = "apikeycollection")
api.add_resource(RoomCollection, "/api/rooms/", endpoint = "roomcollection")
api.add_resource(CustomerItem, "/api/customers/<customer:customer>/", endpoint = "customer")
api.add_resource(CustomerCollection, "/api/customers/", endpoint = "customercollection")
api.add_resource(BookingItem, "/api/bookings/<booking:booking>/", endpoint = "booking")
api.add_resource(BookingCollection, "/api/bookings/", endpoint = "bookingcollection")
