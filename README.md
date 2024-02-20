# PWP SPRING 2024
# Hotel Booking Assistant
# Group information
* Rafiqul Talukder
* Piyumi Weebadu Arachchige
* Julius Norrena

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

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

