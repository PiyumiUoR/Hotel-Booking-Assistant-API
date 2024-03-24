""" Data model (ORM) for Hotel-Booking-Assistant API """

# IMPORTS
import hashlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel_booking_assistant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Hotel(db.Model):

    """ Table for hotels """

    # hotel identifiers
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    # location details
    country = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    street = db.Column(db.String(64), nullable=False)
    # relationships
    rooms = db.relationship("Room", back_populates="hotel")
    admins = db.relationship("Admin", back_populates="hotel")

class Room(db.Model):

    """ Table for rooms """

    # room identifiers
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotel.id", ondelete="SET NULL"))
    number = db.Column(db.Integer)
    # room details
    type = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # relationships
    hotel = db.relationship("Hotel", back_populates="rooms")
    bookings = db.relationship("Booking", back_populates="room")

class Booking(db.Model):

    """ Table for bookings """

    # booking identifiers
    booking_ref = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id", ondelete="SET NULL"))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id", ondelete="SET NULL"))
    # booking details
    check_in = db.Column(db.DATE, nullable=False)
    check_out = db.Column(db.DATE, nullable=False)
    payment = db.Column(db.String(64), nullable=False)
    # relationships
    room = db.relationship("Room", back_populates="bookings")
    customer = db.relationship("Customer", back_populates="bookings")

    @staticmethod
    def json_schema():

        """ Schema validation for a new booking """

        schema = {
            "type": "object",
            "required": ["customer_id", "hotel", "room_type", "payment", "check_in", "check_out"]
        }
        props = schema["properties"] = {}
        props["customer_id"] = {
            "type": "integer"
        }
        props["hotel"] = {
            "type": "string",
        }
        props["room_type"] = {
            "type": "string",
            "enum": ["single", "double", "suite"]
        }
        props["payment"] = {
            "type": "string",
            "enum": ["debit", "credit", "cash"]
        }
        props["check_in"] = {
            "type": "string",
            "format": "date"
        }
        props["check_out"] = {
            "type": "string",
            "format": "date"
        }

        return schema

class Customer(db.Model):

    """ Table for customers """

    # customer identifiers
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    # customer details
    phone = db.Column(db.String(64), nullable=False)
    mail = db.Column(db.String(64), unique=True, nullable=False)
    address = db.Column(db.String(64), nullable=False)
    # relationships
    bookings = db.relationship("Booking", back_populates="customer")

    @staticmethod
    def json_schema():

        """ Schema validation for a new customer """

        schema = {
            "type": "object",
            "required": ["name", "phone", "mail", "address"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "type": "string"
        }
        props["phone"] = {
            "type": "string",
        }
        props["mail"] = {
            "type": "string",
            "format": "email"
        }
        props["address"] = {
            "type": "string",
        }

        return schema

class Admin(db.Model):

    """ Table for administrators """

    # admin identifier
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotel.id", ondelete="SET NULL"))
    # admin credentials
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), nullable=False)
    # relationships
    hotel = db.relationship("Hotel", back_populates="admins")
    apikey = db.relationship("ApiKey", back_populates="admin", uselist=False)

class ApiKey(db.Model):

    """ Table for api keys used in authentication """

    # apikey identifiers
    key = db.Column(db.String(64), primary_key=True, nullable=False)
    admin_username = db.Column(db.String(64), db.ForeignKey("admin.username", ondelete="SET NULL"))

    # relationships
    admin = db.relationship("Admin", back_populates="apikey", uselist=False)

    # method for hashing
    @staticmethod
    def key_hash(key):

        """ Hashing method for api key """

        return hashlib.sha256(key.encode()).hexdigest()

    # validation schema
    @staticmethod
    def json_schema():

        """ Schema validation for api key generation """

        schema = {
            "type": "object",
            "required": ["username", "password"]
        }
        props = schema["properties"] = {}
        props["username"] = {
            "type": "string"
        }
        props["password"] = {
            "type": "string",
        }

        return schema
