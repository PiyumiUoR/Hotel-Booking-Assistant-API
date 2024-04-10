import json
import os
import datetime
from orm import Hotel, Room, Booking, Customer, Admin, app, db
from sqlalchemy import exc

def populate_db():
    # work inside current app context
    with app.app_context():

        # initiate database
        db.create_all()

        # read json for populating the database
        with open(os.getcwd() + "/data.json") as f:
            data = json.load(f)

        # add example customers to the database
        customers = []
        for customer in data["customers"]:
            # create customer entry
            customer_entry = Customer(name=customer["name"], phone=customer["phone"], mail=customer["mail"], address=customer["address"])

            # add customer entry to list
            customers.append(customer_entry)

        # add example hotels to the database
        rooms = []
        hotels = []
        admins = []
        bookings = []
        for hotel in data["hotels"]:

            # append new hotel object to list
            hotel_entry = Hotel(name=hotel["name"], country=hotel["country"], city=hotel["city"], street=hotel["street"])

            # add hotel entry to list
            hotels.append(hotel_entry)

            # add room entry to hotel
            for room in hotel["rooms"]:

                # create room entry
                room_entry = Room(number=room["number"], type=room["type"], price=room["price"], hotel=hotel_entry)

                # add room entry to list
                rooms.append(room_entry)

                # get bookings for each room
                for booking in room["bookings"]:

                    # get booking ref
                    booking_ref = booking["booking_ref"]

                    # create datetime variables for db
                    check_in = booking["check_in"]
                    check_out = booking["check_out"]
                    check_in = datetime.datetime(check_in[0], check_in[1], check_in[2])
                    check_out = datetime.datetime(check_out[0], check_out[1], check_out[2])

                    # find the corresponding customer entry
                    try:
                        # find customer
                        customer = customers[[idx for idx, customer in enumerate(data["customers"]) if booking_ref in customer["bookings"]].pop()]

                        # create new booking entry for customer
                        bookings.append(Booking(booking_ref=booking_ref, check_in=check_in, check_out=check_out, payment=booking["payment"], room=room_entry, customer=customer))

                    except IndexError:
                        print("No customer information available for booking ref: {}. Booking is not added!".format(booking_ref))

            # add admin entry to hotel
            for admin in hotel["admins"]:
                
                # create and add admin entry to list
                admins.append(Admin(username=admin["username"], password=admin["password"], hotel=hotel_entry))
        
        # add all to database
        try:
            db.session.add_all(bookings)
            db.session.add_all(admins)
            db.session.commit()
        except exc.IntegrityError:
            print("Hotel/Room/Admin entry exists in the DB or the data entered is incorrect. Remove the DB and try again!")

def print_db():

    with app.app_context():

        # query hotels and rooms from the database
        for hotel in Hotel.query.all():
            print("\n{} has the following rooms with prices:".format(hotel.name))
            for room in hotel.rooms:
                print("Room type: {}, Price: {} eur".format(room.type, room.price))

        # query all bookings from the database
        print("\n")
        for booking in Booking.query.all():
            print("{} has booked room No. {} in {} from {} to {}".format(booking.customer.name, booking.room.number, booking.room.hotel.name, booking.check_in, booking.check_out))
        
        # query all administrators from the database
        print("\n")
        for admin in Admin.query.all():
            print("{} is an administrator for {}".format(admin.username, admin.hotel.name))

if __name__ == "__main__":

    # populate database from json
    populate_db()

    # print data from database
    print_db()