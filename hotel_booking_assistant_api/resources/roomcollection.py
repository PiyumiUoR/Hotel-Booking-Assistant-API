"""
Resource methods for RoomCollection
"""
import json
from datetime import datetime, timedelta
from flask import Response, request
from flask_restful import Resource
from static.constants import MASON, LINK_RELATIONS_URL
from orm import Hotel, Room, BookingAssistantBuilder, create_error_response
from keyFunc import any_admin

class RoomCollection(Resource):

    """ Class with method for getting room availability information """

    @any_admin
    def get(self):

        """ Get available rooms from Room table (GET) """

        # get country (optional)
        country = request.args.get("country")

        # get city (optional)
        city = request.args.get("city")

        # filter by country and city if given
        if country and city:
            hotels = Hotel.query.filter_by(country=country, city=city).all()
        # filter by country if given
        elif country:
            hotels = Hotel.query.filter_by(country=country).all()
        # filter by city if given
        elif city:
            hotels = Hotel.query.filter_by(city=city).all()
        # if not given, get all hotels
        else:
            hotels = Hotel.query.all()

        # get room type (optional)
        room_type = request.args.get("room_type")

        # get check_in date (optional)
        check_in = request.args.get("check_in")

        # get check_out date (optional)
        check_out = request.args.get("check_out")

        # convert dates if they are given
        if check_in and check_out:
            try:
                check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
            except ValueError:
                return create_error_response(400,
                                             "BadRequest",
                                             "Invalid query parameter value(s)")

            # compute and check length of stay
            duration = check_out - check_in
            days_to_book = [check_in + timedelta(days=day) for day in range(duration.days)]
            if duration.days <= 0:
                return create_error_response(400,
                                             "BadRequest",
                                             "Incorrect check-in/check-out dates")

        # get rooms
        rooms_available = []
        for hotel in hotels:

            # add to list of rooms
            if room_type:
                rooms = Room.query.filter_by(hotel_id=hotel.id, type=room_type).all()
            else:
                rooms = Room.query.filter_by(hotel_id=hotel.id).all()

            # check each room for bookings
            for room in rooms:

                # filter available rooms if check_in and check_out are given
                if check_in and check_out:

                    # list for booked dates
                    dates_booked = []

                    # check the dates of each booking
                    for booking in room.bookings:

                        # get length of booking
                        duration = booking.check_out - booking.check_in

                        # increment the list of booked dates
                        dates_booked.extend(
                        [booking.check_in + timedelta(days=day) for day in range(duration.days)])

                    # check if the room can be booked
                    if any(day_to_book in dates_booked for day_to_book in days_to_book):
                        continue

                # add room information to array of available rooms
                rooms_available.append(room.serialize())

        # return conflict response
        if not rooms_available:
            return create_error_response(409,
                "Conflict",
                "Failure in GET: No rooms fulfilling the criteria are available"
                )

        # return hypermedia response
        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control_add_customer()
        body.add_control_add_bookings()
        body["items"] = rooms_available

        # return available rooms
        return Response(json.dumps(body), status=200, mimetype=MASON)
