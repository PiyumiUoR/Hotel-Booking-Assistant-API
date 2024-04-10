import json
from datetime import date, timedelta
from jsonschema import validate, ValidationError, draft7_format_checker
from werkzeug.exceptions import NotFound, BadRequest, UnsupportedMediaType
from orm import Hotel, Room, Booking, Customer, db, BookingAssistantBuilder
from keyFunc import new_booking_admin
from flask import Response, request, url_for
from flask_restful import Resource
from static.constants import MASON, LINK_RELATIONS_URL

class BookingCollection(Resource):

    """ Class with method for adding new entries to Booking table """

    @new_booking_admin
    def post(self):

        """ Create new Booking entry (POST) """
        
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
            for booking in room.bookings:
                
                # get length of booking
                duration = booking.check_out - booking.check_in

                # increment the list of booked dates
                dates_booked.extend(
                    [booking.check_in + timedelta(days=day) for day in range(duration.days)]
                    )
                
            # check if the room can be booked
            if any(day_to_book in dates_booked for day_to_book in days_to_book):
                continue

            # add new booking entry for room that is available
            booking_entry = Booking(
                check_in=check_in, check_out=check_out,
                payment=payment, room=room, customer=customer
                )

            # add booking to db
            db.session.add(booking_entry)
            db.session.commit()

            # define hypermedia controls
            body = BookingAssistantBuilder()
            body.add_namespace("bookie", LINK_RELATIONS_URL)
            body.add_control_get_booking(booking_entry)
            body.add_control_add_bookings()
            body.add_control_edit_bookings(booking_entry)
            body.add_control_delete_bookings(booking_entry)
            body["item"] = [booking_entry.serialize(short_form=True)]

            # return success response
            return Response(json.dumps(body), status=200, mimetype = MASON)

        # return conflict response
        return "Failure in POST: No room of the requested type is available", 409
