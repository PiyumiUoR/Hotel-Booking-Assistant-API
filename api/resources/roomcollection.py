import json
from datetime import datetime, timedelta
from orm import Hotel, Room, BookingAssistantBuilder
from keyFunc import any_admin
from flask import Response, request
from flask_restful import Resource
from static.constants import MASON, LINK_RELATIONS_URL

class RoomCollection(Resource):

    """ Class with method for getting room availability information """

    @any_admin
    def get(self, country, city):

        """ Get available rooms from Room table (GET) """

        # get hotels and possible rooms
        hotels = Hotel.query.filter_by(country=country, city=city).all()

        # get query parameters
        try:
            room_type = request.args["room_type"]
        except KeyError:
            return "Missing query parameter: room_type", 400
        
        # get check_in date
        try:
            check_in = request.args["check_in"]
        except KeyError:
            return "Missing query parameter: check_in", 400
        
        # get check_out date
        try:
            check_out = request.args["check_out"]
        except KeyError:
            return "Missing query parameter: check_out", 400
        
        # convert to date
        try:
            check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid query parameter value(s)", 400
        
        # compute and check length of stay
        duration = check_out - check_in
        days_to_book = [check_in + timedelta(days=day) for day in range(duration.days)]
        if duration.days <= 0:
            return "Incorrect check-in/check-out dates", 400

        # get rooms
        rooms_available = []
        for hotel in hotels:
            
            # add to list of rooms
            rooms = Room.query.filter_by(hotel_id=hotel.id, type=room_type).all()

            # check each room for bookings
            for room in rooms:
                
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
                rooms_available.append(room.serialize(short_form=True))         

        # return conflict response
        if not rooms_available:
            return "Failure in GET: No rooms fulfilling the criteria are available", 409
        
        # return hypermedia response
        body = BookingAssistantBuilder()
        body.add_namespace("bookie", LINK_RELATIONS_URL)
        body.add_control_avl_rooms(country, city)
        body["items"] = rooms_available
        
        # return available rooms
        return Response(json.dumps(body), status=200, mimetype = MASON)