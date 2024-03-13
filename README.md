# PWP SPRING 2024
# Hotel Booking Assistant
# Group information
* Rafiqul Talukder
* Piyumi Weebadu Arachchige
* Julius Norrena

# Hotel Booking Assistant

This Flask application serves as a hotel booking assistant, managing hotel, room, booking, customer, and admin information in a database.

## Dependencies

To run this Flask based application please install the dependencies mentioned bellow:

- Flask: `pip install Flask`(for more information check: https://flask.palletsprojects.com/en/3.0.x/)    
- Flask-SQLAlchemy: `pip install Flask-SQLAlchemy` (for more information check: https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/)

## Database

The application uses SQLite as the database. SQLAlchemy is the ORM (Object-Relational Mapping) library for interacting with the database.

### Database Setup

1. **Install SQLite:**
   - Follow the instructions on the [SQLite website](https://www.sqlite.org/download.html) to download and install SQLite for your operating system.
   - during our test run we used SQLite version 3.41.2

2. **Create a Virtual Environment:**
   - It's recommended to create a virtual environment for your project. Run the following commands:
     ```
     On MacOS / Linux (bash)
     python -m venv venv
     source venv/bin/activate
     
     On Windows, use 'venv\Scripts\activate'
     ```
     For more information about python vertual environment please check: https://docs.python.org/3/library/venv.html

3. **Install Dependencies:**
   - Install the required dependencies using:
     ```bash
     pip install -r requirements.txt
     ```
     
More infomation about specific version of Flask and other technologies can be found in requirements.txt file

### Populate Database

To populate the database with sample data:

1. Ensure that `data.json` is in the same directory as `hotel_booking_assistant.db`, `orm.py` & `polulate.py`.
2. Run the `populatedb.py` script.


# RESTful API Functional Testing

To run the test you need to run:
```bash
ipython test.py
``` 

## Test Cases

### Test Case 1: Get Customer Information
Description: Tests the /api/customers/{customer_id}/ endpoint to retrieve customer information.
Expected Outcome: The API should return the customer information if the customer exists, or a 404 error if the customer does not exist.

### Test Case 2: Get Available Rooms
Description: Tests the /api/hotels/{country}/{city}/rooms/ endpoint to retrieve available rooms.
Expected Outcome: The API should return a list of available rooms for the specified criteria, or a message indicating no rooms are available.

### Test Case 3: Booking Information
Description: Tests the /api/bookings/{booking_ref}/ endpoint to retrieve booking information.
Expected Outcome: The API should return the booking information if the booking exists, or a 404 error if the booking does not exist.

### Test Case 4: Delete Booking
Description: Tests the /api/bookings/{booking_ref}/ endpoint to delete a booking.
Expected Outcome: The API should return a 204 status code if the booking is successfully deleted, a 404 error if the booking does not exist, or an appropriate error if there's any other issue.

### Test Case 5: Get Nonexistent Booking
Description: Tests the /api/bookings/{booking_ref}/ endpoint to retrieve information about a nonexistent booking.
Expected Outcome: The API should return a 404 error indicating that the booking does not exist.

### Test Case 6: Create Customer
Description: Tests the /api/customers/ endpoint to create a new customer.
Expected Outcome: The API should return a 201 status code if the customer is successfully created, a 409 error if the email is already in use, or an appropriate error if there's any other issue.
