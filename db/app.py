""" Hotel-Booking-Assistant API """

# IMPORTS
import json
import secrets
from datetime import date, datetime, timedelta
from jsonschema import validate, ValidationError, draft7_format_checker
from werkzeug.exceptions import NotFound, BadRequest, UnsupportedMediaType
from werkzeug.routing import BaseConverter
from flask import Response, request
from flask_restful import Api, Resource
from sqlalchemy import exc
from orm import Hotel, Room, Booking, Customer, Admin, ApiKey, app, db
from keyfunc import booking_specific_admin, new_booking_admin, customer_admin, any_admin

class CustomerConverter(BaseConverter):

    """ Converter for the Customer class """

    def to_python(self, value):

        customer_db = Customer.query.filter_by(id=value).first()
        if customer_db is None:
            raise NotFound
        return customer_db

    def to_url(self, value):
        return str(value.id)

class BookingConverter(BaseConverter):

    """ Converter for the Booking class """

    def to_python(self, value):

        booking_db = Booking.query.filter_by(booking_ref=value).first()
        if booking_db is None:
            raise NotFound
        return booking_db

    def to_url(self, value):
        return str(value.booking_ref)

class ApiKeyCollection(Resource):

    """ Class with methods for deleting and adding new entries to ApiKey table """

    @any_admin
    def delete(self):

        """ Delete existing ApiKey entry (DELETE) """

        # get apikey of admin
        apikey = ApiKey.query.filter_by(admin_username=request.headers["Admin-User-Name"]).first()

        # delete customer
        db.session.delete(apikey)
        db.session.commit()

        # return response
        return Response(status=204)

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

        # add apikey to database
        db.session.add(apikey_entry)
        db.session.commit()

        # return success response
        return Response(status=201, headers={"Hotels-Api-Key": token})

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

        # return success response
        return Response(status=201,
                        headers={"Location": api.url_for(CustomerItem, customer=customer_entry)})

class CustomerItem(Resource):

    """ Class with methods for getting, deleting and modifying Customer information """

    @customer_admin
    def get(self, customer):

        """ Get Customer entry (GET) """

        body = {
            "name": customer.name,
            "phone": customer.phone,
            "mail": customer.mail,
            "address": customer.address
        }

        return Response(json.dumps(body), status=200, mimetype="application/json")

    # delete customer
    @customer_admin
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

        # return response
        return Response(status=204)

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

        return Response(status=204)

class RoomCollection(Resource):

    """ Class with method for getting room availability information """

    @any_admin
    def get(self, country, city):

        """ Get available rooms from Room table (GET) """

        # get hotels and possible rooms
        hotels = Hotel.query.filter_by(country=country, city=city).all()

        # get query parameters
        try:
            room_type = request.args["room"]
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
                rooms_available.append({
                    "Hotel": room.hotel.name, "Country": room.hotel.country,
                    "City": room.hotel.city,"Address": room.hotel.street, "Price": room.price
                    })

        # return conflict response
        if not rooms_available:
            return "Failure in GET: No rooms fulfilling the criteria are available", 409

        # return available rooms
        return Response(json.dumps(rooms_available), status=200, mimetype="application/json")

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

            # return success response
            return Response(
                status=201, headers={"Location": api.url_for(BookingItem, booking=booking_entry)}
                )

        # return conflict response
        return "Failure in POST: No room of the requested type is available", 409

class BookingItem(Resource):

    """ Class with methods for getting, deleting and modifying Booking information """

    @booking_specific_admin
    def get(self, booking):

        """ Get Booking entry (GET) """

        body = {
            "hotel": booking.room.hotel.name,
            "room": booking.room.number,
            "customer": booking.customer.name,
            "check-in": str(booking.check_in),
            "check-out": str(booking.check_out)
        }

        return Response(json.dumps(body), status=200, mimetype="application/json")

    @booking_specific_admin
    def delete(self, booking):

        """ Delete existing Booking entry (DELETE) """

        # delete booking
        db.session.delete(booking)
        db.session.commit()

        # return response
        return Response(status=204)

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

            # return success response
            return Response(status=204)

        # return conflict response
        return "No rooms corresponding to the criteria are available", 409

@app.route("/")
def index():

    """ Front page """

    return "Hotel Booking Assistant API"

# API RESOURCES, CONVERTERS AND URIs
api = Api(app)
app.url_map.converters["customer"] = CustomerConverter
app.url_map.converters["booking"] = BookingConverter
api.add_resource(ApiKeyCollection, "/api/keys/")
api.add_resource(RoomCollection, "/api/rooms/<string:country>/<string:city>/")
api.add_resource(CustomerItem, "/api/customers/<customer:customer>/")
api.add_resource(CustomerCollection, "/api/customers/")
api.add_resource(BookingItem, "/api/bookings/<booking:booking>/")
api.add_resource(BookingCollection, "/api/bookings/")
