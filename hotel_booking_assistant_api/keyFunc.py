""" Authentication methods for Hotel-Booking-Assistant API """

# IMPORTS
import secrets
from werkzeug.exceptions import HTTPException
from flask import request
from orm import ApiKey, create_error_response

def new_booking_admin(func):

    """ wrapper for authentication regarding new bookings """
    def wrapper(self, *args, **kwargs):

        """
        Authorization for following request types: BookingCollection: POST; BookingItem: PUT
        Key must match the key of the admin for the hotel in question
        """

        # get hashed key from headers
        apikey = request.headers.get("Hotels-Api-Key")
        if apikey is None:
            raise HTTPException(
                response=create_error_response(
                    400,
                    "BadRequest",
                    "Header (Hotels-Api-Key) was not provided!")
                    )

        # get admin username
        username = request.headers.get("Admin-User-Name")
        if username is None:
            raise HTTPException(response=create_error_response(
                400,
                "BadRequest",
                "Header (Admin-User-Name) was not provided!")
                )

        hotel = request.json.get("hotel")
        if hotel is None:
            raise HTTPException(response=create_error_response(
                400,
                "BadRequest",
                "Hotel was not provided in request body!")
                )

        # get hash for the apikey given
        apikey_hash = ApiKey.key_hash(apikey)

        # get hash from the database
        apikey_db = ApiKey.query.filter_by(admin_username=username).first()

        # check that an apikey was found
        if apikey_db is None:
            raise HTTPException(
                response=create_error_response(
                    403,
                    "Forbidden",
                    "Admin has no API key!")
                )

        # check for matching hash
        if secrets.compare_digest(apikey_hash, apikey_db.key):
            # check if the matching admin is actually authorized for the hotel
            if apikey_db.admin.hotel.name == hotel:
                return func(self, *args, **kwargs)

        # unauthorized (no match)
        raise HTTPException(response=create_error_response(
            403,
            "Forbidden",
            "Admin is unauthorized!")
            )

    return wrapper

def booking_specific_admin(func):

    """ wrapper for authentication regarding existing bookings """
    def wrapper(self, booking, *args, **kwargs):

        """ 
        Authorization for following request types: BookingItem: GET, DELETE
        Key must match the key of the admin for the hotel of the original booking
        """

        # get hashed key from headers
        apikey = request.headers.get("Hotels-Api-Key")
        if apikey is None:
            raise HTTPException(
                response=create_error_response(
                    400,
                    "BadRequest",
                    "Header (Hotels-Api-Key) was not provided!")
                    )

        username = request.headers.get("Admin-User-Name")
        if username is None:
            raise HTTPException(response=create_error_response(
                400,
                "BadRequest",
                "Header (Admin-User-Name) was not provided!")
                )

        # get hash for the apikey given
        apikey_hash = ApiKey.key_hash(apikey)

        # get hash from the database
        apikey_db = ApiKey.query.filter_by(admin_username=username).first()

        # check that an apikey was found
        if apikey_db is None:
            raise HTTPException(
                response=create_error_response(
                    403,
                    "Forbidden",
                    "Admin has no API key!")
                    )

        # check for matching hash
        if secrets.compare_digest(apikey_hash, apikey_db.key):
            # check if the matching admin is actually authorized for the hotel
            if apikey_db.admin_username in [
                admin_entry.username for admin_entry in booking.room.hotel.admins
                ]:

                # successful validation
                return func(self, booking, *args, **kwargs)

        # return response with unauthorized
        raise HTTPException(response=create_error_response(
            403,
            "Forbidden",
            "Admin is unauthorized!")
            )

    return wrapper

def any_admin(func):

    """ wrapper for general authentication """
    def wrapper(self, *args, **kwargs):

        """
        Authorization for following request types: CustomerCollection: POST; RoomCollection: GET
        Key can match any of the admins keys as long as the admin username and key also match
        """

        # get hashed key from headers
        apikey = request.headers.get("Hotels-Api-Key")
        if apikey is None:
            raise HTTPException(
                response=create_error_response(
                    400,
                    "BadRequest",
                    "Header (Hotels-Api-Key) was not provided!")
                    )

        username = request.headers.get("Admin-User-Name")
        if username is None:
            raise HTTPException(response=create_error_response(
                400,
                "BadRequest",
                "Header (Admin-User-Name) was not provided!")
                )

        # get hash for the apikey given
        apikey_hash = ApiKey.key_hash(apikey)

        # get hash from the database
        apikey_db = ApiKey.query.filter_by(admin_username=username).first()

        # check that an apikey was found
        if apikey_db is None:
            raise HTTPException(response=create_error_response(
                403,
                "Forbidden",
                "Admin has no API key!")
                )

        # check for matching hash
        if secrets.compare_digest(apikey_hash, apikey_db.key):
            # check if the matching admin is actually authorized for the hotel
            return func(self, *args, **kwargs)

        # return response with unauthorized
        raise HTTPException(response=create_error_response(
            403,
            "Forbidden",
            "Admin is unauthorized!")
            )

    return wrapper
