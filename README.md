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

1. Ensure that `data.json` is in the same directory as `app.py`, `keyFunc.py`, `orm.py`, `populate.py` and `test_app.py`.
2. Run the `populate.py` script.


# Testing

## Preparing testing environment
If you already have installed Dependencies skip step 1 and continue from step 2

1. **Install Dependencies:**
   - Install the required dependencies using:
     ```bash
     pip install -r requirements.txt
     ```

2. **Run Local Development Server for Flask Application**
    - run `flask run` in your console / terminal. It will start a local development server

3. **Start Testing**
    - run `test_app.py` file with pytest:
    ```
    pytest --cov .
    ```
4 **Detailed Test Report**
    - To get a detailed test report run:
    ```
    coverage html
    ```
    The coverage html command is part of the Coverage.py tool, which is used for measuring code coverage of Python programs.
    This command specifically generates an HTML report that visually represents the code coverage of your tests.
    
## Test Coverage Report
On April 9, 2024 our comprehensive API testing achieved an impressice 94% overall code coverage, this ensures a high level of code quality and reliability for this Hotel Booking Assistent API.

### About Test Coverage Report:
![Test Coverage Report](https://github.com/RafiqulT1/PWP/blob/main/images/Coverage%20report.png)

### Highlights:
Our core application logic in app.py and utility constants in static/constants.py have achieved 100% coverage, ensuring that our foundational code is thoroughly tested.
The comprehensive tests in test_app.py also got a perfect coverage, highlighting the effectiveness of our testing strategy.

### Areas for Improvement:
The majority of our resource modules exhibit good coverage, yet there is space for development in resources/customeritem.py and resources/bookingcollection.py.

