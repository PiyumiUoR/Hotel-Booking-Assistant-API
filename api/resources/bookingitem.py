import json
from datetime import date, timedelta
from jsonschema import validate, ValidationError, draft7_format_checker
from werkzeug.exceptions import NotFound, BadRequest, UnsupportedMediaType
from orm import Hotel, Room, Booking, Customer, db, BookingAssistantBuilder
from keyFunc import booking_specific_admin, new_booking_admin
from flask import Response, request, url_for
from flask_restful import Resource
from static.constants import MASON, LINK_RELATIONS_URL, BOOKING_DETAILS_URL

class BookingItem(Resource):

    """ Class with methods for getting, deleting and modifying Booking information """

    @booking_specific_admin
    def get(self, booking):

        """ Get Booking entry (GET) """

        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control("self", href = BOOKING_DETAILS_URL)
        body.add_control_get_booking(booking)
        body.add_control_edit_bookings(booking)
        body.add_control_delete_bookings(booking)
        body.add_control_add_bookings()
        body.add_control("bookingcollection", url_for("bookingcollection"))

        body["item"] = [booking.serialize(short_form=True)]

        return Response(json.dumps(body), status=200, mimetype= MASON)
    
    @booking_specific_admin
    def delete(self, booking):

        """ Delete existing Booking entry (DELETE) """
        
        # delete booking
        db.session.delete(booking)
        
        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control_add_bookings()

        db.session.commit()
        # return response
        return Response(json.dumps(body), status=200, mimetype = MASON)
    
    @new_booking_admin
    def put(self, booking):

        """ Modify existing Booking entry (PUT) """
        
        # check request type
        if request.headers["Content-Type"] != "application/json":
            raise UnsupportedMediaType
        
        # validate request format
        try:
            validate(request.json, Booking.json_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        # get hotel instance
        hotel = Hotel.query.filter_by(name=request.json["hotel"]).first()
        if hotel is None:
            raise NotFound
        
        # create dates from request data
        check_in = date.fromisoformat(request.json["check_in"])
        check_out = date.fromisoformat(request.json["check_out"])

        # get customer instance
        customer = Customer.query.filter_by(id=request.json["customer_id"]).first()
        if customer is None:
            raise NotFound

        # get payment information
        payment = request.json["payment"]

        # compute and check length of stay
        duration = check_out - check_in
        days_to_book = [check_in + timedelta(days=day) for day in range(duration.days)]
        if duration.days <= 0:
            return "Incorrect check-in/check-out dates", 400
        
        # get possible rooms for booking
        rooms = Room.query.filter_by(hotel_id=hotel.id, type=request.json["room_type"]).all()
        if not rooms:
            raise NotFound

        # find out availability of room
        for room in rooms:

            # initialize list for booked dates
            dates_booked = []

            # get booked dates
            for room_booking in room.bookings:
                
                # get length of booking
                duration = room_booking.check_out - room_booking.check_in

                # increment the list of booked dates
                dates_booked.extend(
                    [room_booking.check_in + timedelta(days=day) for day in range(duration.days)]
                    )
                
            # check if the room can be booked
            if any(day_to_book in dates_booked for day_to_book in days_to_book):
                continue

            # modify booking entry
            booking.check_in = check_in
            booking.check_out = check_out
            booking.payment = payment
            booking.room = room
            booking.customer = customer
            db.session.commit()

            body = BookingAssistantBuilder()
            body.add_namespace("bookie", LINK_RELATIONS_URL)
            # body.add_control("self", href = CUSTOMER_PROFILE_URL)
            body.add_control_get_booking(booking)
            body.add_control_add_bookings()
            body.add_control_edit_bookings(booking)
            body.add_control_delete_bookings(booking)
            
            body["item"] = [booking.serialize(short_form=True)]


            # return success response
            return Response(json.dumps(body), status=200, mimetype = MASON)

        # return conflict response
        return "No rooms corresponding to the criteria are available", 409