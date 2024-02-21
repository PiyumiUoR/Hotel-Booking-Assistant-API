from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel_booking_assistant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Hotel(db.Model):
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
    # room identifiers
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotel.id", ondelete="SET NULL")) 
    number = db.Column(db.Integer)
    # room details
    type = db.Column(db.String(64), nullable=False)
    available = db.Column(db.Boolean(), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # relationships
    hotel = db.relationship("Hotel", back_populates="rooms")
    bookings = db.relationship("Booking", back_populates="room")

class Booking(db.Model):
    # booking identifiers
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_ref = db.Column(db.Integer, unique=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id", ondelete="SET NULL"))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id", ondelete="SET NULL"))
    # booking details
    check_in = db.Column(db.DATETIME, nullable=False)
    check_out = db.Column(db.DATETIME, nullable=False)
    payment = db.Column(db.String(64), nullable=False)
    # relationships
    room = db.relationship("Room", back_populates="bookings")
    customer = db.relationship("Customer", back_populates="bookings")

class Customer(db.Model):
    # customer identifiers
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    # customer details
    phone = db.Column(db.String(64), nullable=False)
    mail = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64), nullable=False)
    # relationships
    bookings = db.relationship("Booking", back_populates="customer")

class Admin(db.Model):
    # admin identifier
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotel.id", ondelete="SET NULL"))
    # admin credentials
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), nullable=False)
    # relationships
    hotel = db.relationship("Hotel", back_populates="admins")
