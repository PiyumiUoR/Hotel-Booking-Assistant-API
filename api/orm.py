""" Data model (ORM) for Hotel-Booking-Assistant API """

# IMPORTS
import hashlib
from flask import Flask, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
# from utils import BookingAssistantBuilder
from static.constants import LINK_RELATIONS_URL, CUSTOMER_PROFILE_URL, BOOKING_DETAILS_URL

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel_booking_assistant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SWAGGER"] = {
    "title": "Booking Assistant API",
    "openapi": "3.0.3",
    "uiversion": 3,
    "doc_dir": "./doc"
}
swagger = Swagger(app, template_file="doc/bookingassistant.yml")
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

    def serialize(self, short_form = False):
        data = BookingAssistantBuilder(
            hotel_name = self.hotel.name,
            hotel_address = self.hotel.street,
            room_type = self.type,
            price = self.price
        )
        data.add_control_avl_rooms(self.hotel.country, self.hotel.city)

        return data    

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

    def serialize(self, short_form = False):
        data = BookingAssistantBuilder(
            booking_ref = self.booking_ref,
            room_id = self.room_id,
            customer_id = self.customer_id,
            check_in = self.check_in and self.check_in.isoformat(),
            check_out = self.check_out and self.check_out.isoformat(),
            payment = self.payment
        )
        if short_form:
            data.add_control("self", url_for("booking", booking = self))
            return data
        
        data.add_namespace("bookie", LINK_RELATIONS_URL)
        data.add_control_edit_bookings(self)
        data.add_control_delete_bookings(self)

        return data

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

    def serialize(self, short_form = False):
        data = BookingAssistantBuilder(
            id = self.id,
            name = self.name,
            phone = self.phone,
            mail = self.mail,
            address = self.address
        )
        
        if short_form:
            data.add_control("self", url_for("customer", customer = self))
            return data
        
        data.add_namespace("bookie", LINK_RELATIONS_URL)

        return data

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

    def serialize(self):
        data = BookingAssistantBuilder(
            username = self.username,
            password = self.password
        )
        data.add_control_add_apikey()
        return data

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
    
    def serialize(self, short_form = False):
        data = BookingAssistantBuilder(
            key = self.key,
            admin_username = self.admin_username
        )
        if short_form:
            data.add_control("self", url_for("apikeycollection"))
            return data

        data.add_namespace("bookie", LINK_RELATIONS_URL)
        data.add_control_add_apikey(self)

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

class MasonBuilder(dict):
    def add_namespace(self, ns, uri):
        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }
    
    def add_control(self, ctrl_name, href, **kwargs):
        if "@controls" not in self:
            self["@controls"] = {}
        
        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

    def add_error(self, title, details):
       self["@error"] = {
            "@message": title,
            "@messages": [details],
        }
    
    def add_control_get(self, ctrl_name, title, href):
        self.add_control(
            ctrl_name,
            href,
            method = "GET",
            title = title
        )

    def add_control_post(self, ctrl_name, title, href, schema):
        self.add_control(
            ctrl_name,
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_put(self, ctrl_name, title, href, schema):        
        self.add_control(
            ctrl_name,
            href,
            method="PUT",
            encoding="json",
            title=title,
            schema=schema
        )
    
    def add_control_delete(self, ctrl_name, title, href):
        
        self.add_control(
            ctrl_name,
            href,
            method="DELETE",
            title=title,
        )

class BookingAssistantBuilder(MasonBuilder):
    def add_control_get_customer(self, customer):
        self.add_control_get(
            "bookie:customer-details",
            "Details of the customer",
            url_for("customer", customer = customer)
        )

    def add_control_add_customer(self):
        self.add_control_post(
            "bookie:add-customer",
            "Add new customer",
            url_for("customercollection"),
            Customer.json_schema()
        )
    
    # TODO - Test
    def add_control_delete_customer(self, customer):
        self.add_control_delete(
            "bookie:delete-customer",
            "Delete the customer",
            url_for("customer", customer = customer)            
        )

    def add_control_edit_customer(self, customer):        
        self.add_control_put(
            "bookie: edit-customer",
            "Update customer",
            url_for("customer", customer = customer),
            Customer.json_schema()
        )

    def add_control_get_booking(self, booking):
        self.add_control_get(
            "bookie:booking-details",
            url_for("booking", booking = booking),
            "Details of the booking"
        )

    def add_control_delete_bookings(self, booking):
        self.add_control_delete(
            "bookie:delete-booking",
            "Delete booking",
            url_for("booking", booking = booking)
        )

    def add_control_add_bookings(self):
        self.add_control_post(
            "bookie:add-booking",
            "Add new booking",
            url_for("bookingcollection"),
            Booking.json_schema()
        )
    
    def add_control_edit_bookings(self, booking):
        self.add_control_put(
            "bookie:edit-booking",
            "Add new booking",
            url_for("booking", booking = booking),            
            Booking.json_schema()            
        )
    
    def add_control_add_apikey(self):
        self.add_control_post(
            "bookie:add-apikey",
            "Add a new Api Key",
            url_for("apikeycollection"),
            ApiKey.json_schema()
        )

    def add_control_delete_apikey(self, apikey):
        self.add_control_delete(
            "bookie:delete-apikey",
            "Delete API key",
            url_for("apikeycollection")
        )


    def add_control_avl_rooms(self, country, city):
        self.add_control_get(
            "bookie:room-avl",
            "Available rooms",
            url_for("roomcollection", country = country, city = city)            
        )

