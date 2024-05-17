import pytest
import json
import tempfile
import os
from flask import Flask, url_for
from flask import json
from sqlalchemy import event
from sqlalchemy.orm import close_all_sessions
from orm import db, app, Hotel, Room, Booking, Customer, Admin, ApiKey
from populate import populate_db, print_db
from werkzeug.exceptions import NotFound
from app import app as flask_app, db
import requests
BASE_URL = "http://127.0.0.1:5000/"



def apply_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def add_admin_and_api_key(): #creating test_apikey before hand to test apikey addition to the database through test_populate_db()
    """Adds an admin user and an associated ApiKey record for testing."""
    with app.app_context():
        # Create an Admin
        test_admin = Admin(username="testi_admin", password="tesi_pass", hotel_id=Hotel.query.first().id)
        db.session.add(test_admin)
        db.session.commit()

        # Create an ApiKey associated with the Admin
        test_api_key = ApiKey(key="test_apikey", admin_username=test_admin.username)
        db.session.add(test_api_key)
        db.session.commit()



@pytest.fixture #fixer sets up a temporary test environment and database
def test_client():
    db_fd, db_fname = tempfile.mkstemp() # creats temporary database file
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname 
    app.config["TESTING"] = True # sets Flask app to run in testing mode

    with app.app_context(): 
        event.listen(db.engine, "connect", apply_sqlite_foreign_keys) # this function enables foreign key support on database connection
        db.create_all() #creats database table
        populate_db() # populate the database with the initial data
        add_admin_and_api_key()  #ensure an Admin and Apikey is present

    yield app.test_client() #create test client for making requests to the Flask application

    with app.app_context():
        close_all_sessions()
        db.drop_all()

    os.close(db_fd) #cleans filesystem
    os.unlink(db_fname) #and delete the temporary file

def test_populate_db(test_client): #fixer generated test client
    with app.app_context(): 
        assert Hotel.query.count() > 0, "No hotel data added." #checks if data has been add to the database
        assert Room.query.count() > 0, "No rooms data added."
        assert Customer.query.count() > 0, "No customer data added."
        assert Booking.query.count() > 0, "No booking data added."
        assert Admin.query.count() > 0, "No admin data added."
        assert ApiKey.query.count() > 0, "No api data added" 
        
def test_print_db_executes(test_client, capsys):
    with app.app_context():
        print_db()

    # capture console print
    captured_output = capsys.readouterr()

    # add captured console print to a variable
    output_from_print_db = captured_output.out

    # Check if the output has "Hotel" init
    contains_hotel = "Hotel" in output_from_print_db

    # Check if the output has "No data in database." init
    contains_no_data_message = "No data in database." in output_from_print_db


    if contains_hotel or contains_no_data_message:
        assert True

    

# ------------------ API RESPONSE TESTING --------------

@pytest.fixture
def api_credentials():
    ADMIN_USERNAME = "heikki"
    ADMIN_PASSWORD = "root"
    api_key = generate_api_key(ADMIN_USERNAME, ADMIN_PASSWORD) 
    print(api_key)
    yield api_key, ADMIN_USERNAME

def generate_api_key(username, password):
    """
    Test case for generating an API key for an admin.
    """
    print("TEST: generate_api_key")
    
    
    url = f"{BASE_URL}api/keys/"
    credentials = {"username": username, "password": password}

    response = requests.post(url, json=credentials)
    
    if response.status_code == 201:
        api_key = response.headers.get("Hotels-Api-Key")
        # api_key = response.json().get("item")[0].get("key")
        # print(f"API Key generated successfully: {api_key}")
        return api_key



# Test api key generation
@pytest.mark.parametrize("username, password", [
    ("heikki", "root"),
    ("juho", "test"),  
])
def test_api_key_collection_post(test_client, username, password):
    
    url = '/api/keys/'
    admin_data = {
        "username": username,
        "password": password
    }
    response = test_client.post(url, json=admin_data)
    assert response.status_code in [201, 401], f"Unexpected status code returned: {response.status_code}"
    

# Test dual api key generation
@pytest.mark.parametrize("username, password", [
    ("heikki", "root"),
    ("juho", "test"),  
])
def test_api_key_collection_post_dual_apikey(test_client, username, password):
    generate_api_key(username, password)
    
    url = '/api/keys/'
    admin_data = {
        "username": username,
        "password": password
    }
    response = test_client.post(url, json=admin_data)
    assert response.status_code in [401, 409], f"Unexpected status code returned: {response.status_code}"



# test api key deletion
def test_api_key_collection_delete(test_client, api_credentials):
    api_key, admin_username = api_credentials
    
    url = '/api/keys/'
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }
    response = test_client.delete(url, headers=headers)
    
    # Check for successful API key deletion (204 No Content)
    assert response.status_code == 204, "Failed to delete API key"

#test api key deletion without credentials
def test_api_key_collection_delete_no_apikey_username(test_client):
    url = '/api/keys/'
    response = test_client.delete(url)
    assert response.status_code in [404,400], "Failed to delete API key"

#test api key deletion without username
def test_api_key_collection_delete_no_username(test_client, api_credentials):
    api_key = api_credentials
    
    url = '/api/keys/'
    headers = {
        "Hotels-Api-Key": api_key,
    }
    response = test_client.delete(url, headers=headers)
    
    assert response.status_code in [404,400], "Failed to delete API key"

#test api key deletion without apikey
def test_api_key_collection_delete_no_apikey(test_client, api_credentials):
    admin_username = api_credentials
    url = '/api/keys/'
    headers = {
        "Hotels-Api-Key": None,
        "Admin-User-Name": admin_username
    }
    response = test_client.delete(url, headers=headers)
    assert response.status_code in [403,400], "Failed to delete API key"



# # Test get home_page
# def test_root_endpoint(test_client):
#     # Make a GET request to the root endpoint "/"
#     response = test_client.get('/api/')
#     # Check that the response status code is 200 (OK)
#     assert response.status_code == 200
#     # Check that the response data matches the expected result
#     assert response.data.decode('utf-8') == "Hotel Booking Assistant API"
 
# Test entry_point
def test_entry_point(test_client):
    response = test_client.get('/api/')

    # Verify the response status code is 200 OK
    assert response.status_code == 200, "Expected status code 200 OK, got: {}".format(response.status_code)


 
# Test create new customer
@pytest.mark.parametrize("customer_data", [
    {"name": "John Doe", "phone": "1234567890", "mail": "john.doe@example.com", "address": "123 Main St"},
    {"name": "Matti Meikalainen", "mail": "matti.meikalainen@gmail.com", "phone": "1234567890", "address": "Matintie 1"},
    # Add more customer data dictionaries here to test various input cases
])
def test_customer_collection_post(test_client, api_credentials, customer_data):
    api_key, admin_username = api_credentials

    url = '/api/customers/'
    response = test_client.post(url, headers={
        "Content-Type": "application/json",
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    }, data=json.dumps(customer_data))

    # Assert the response status code is 201 Created
    assert response.status_code in [201, 409], f"Unexpected status code returned: {response.status_code}"


# test GET customer info
@pytest.mark.parametrize("customer_id", [1, 2, 1000])
def test_customer_item_get(test_client, api_credentials, customer_id):
    api_key, admin_username = api_credentials

    response = test_client.get(f'/api/customers/{customer_id}/', headers={
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    })
    assert response.status_code in [200, 404, 403], f"Unexpected status code returned: {response.status_code}"
    
# test GET customer info without username
@pytest.mark.parametrize("customer_id", [1])
def test_customer_item_get_no_username(test_client, api_credentials, customer_id):
    api_key = api_credentials
    response = test_client.get(f'/api/customers/{customer_id}/', headers={
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": None
        
    })
    assert response.status_code in [400, 403], f"Unexpected status code returned: {response.status_code}"
    
# test GET customer info without apikey
@pytest.mark.parametrize("customer_id", [1])
def test_customer_item_get_no_apikey(test_client, api_credentials, customer_id):
    admin_username = api_credentials
    response = test_client.get(f'/api/customers/{customer_id}/', headers={
        "Hotels-Api-Key": None,
        "Admin-User-Name": admin_username
    })
    assert response.status_code in [400, 403], f"Unexpected status code returned: {response.status_code}"
    
#test GET customer info without credentials   
@pytest.mark.parametrize("customer_id", [1])
def test_customer_item_get_no_apikey_username(test_client, api_credentials, customer_id):
    response = test_client.get(f'/api/customers/{customer_id}/')
    assert response.status_code in [400, 404], f"Unexpected status code returned: {response.status_code}"


#test customer info deletion
@pytest.mark.parametrize("customer_id", [1, 2, 1000])
def test_customer_item_delete(test_client, api_credentials, customer_id):
    api_key, admin_username = api_credentials


    response = test_client.delete(f'/api/customers/{customer_id}/', headers={
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    })
    
    assert response.status_code in [204, 403, 405, 404], f"Unexpected status code returned: {response.status_code}"
        


#test updating customer info and test if email already in use
@pytest.mark.parametrize("customer_id, update_data", [
    (1, {"name": "Jane Updated", "mail": "jane.updated@example.com", "phone": "987654321", "address": "123 Updated Street"}),
    (1, {"name": "Matti Meikalainen", "mail": "matti.meikalainen@gmail.com", "phone": "1234567890", "address": "Matintie 1"}),
    (2, {"name": "Matti Meikalainen", "mail": "matti.meikalainen@gmail.com", "phone": "1234567890", "address": "Matintie 1"}),
    (100, {"name": "Matti Meikalainen", "mail": "matti.meikalainen@gmail.com", "phone": "1234567890", "address": "Matintie 1"}),
])
def test_customer_item_put(test_client, api_credentials, customer_id, update_data):
    api_key, admin_username = api_credentials
    
    response = test_client.put(f'/api/customers/{customer_id}/', headers={
        "Content-Type": "application/json",
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    }, data=json.dumps(update_data))

    assert response.status_code in [204, 409, 404, 403], f"Unexpected status code returned: {response.status_code}"


#test updating customer info without username
@pytest.mark.parametrize("customer_id, update_data", [
    (1, {"name": "Jane Updated", "mail": "jane.updated@example.com", "phone": "987654321", "address": "123 Updated Street"}),
])
def test_customer_item_put_no_apikey_username(test_client, customer_id, update_data):
    api_key = api_credentials
    
    response = test_client.put(f'/api/customers/{customer_id}/', headers={
        "Hotels-Api-Key": api_key,
    }, data=json.dumps(update_data))

    assert response.status_code in [400, 404], f"Unexpected status code returned: {response.status_code}"
    


@pytest.mark.parametrize("country_city_room_date", [
    ("Finland", "Oulu", "single", "2024-03-10", "2024-03-15"),  
    ("Testi", "testi", "testi", "2025-03-10", "2025-03-15"), 
])
def test_room_collection_get_200_409(test_client, api_credentials, country_city_room_date):
    country, city, room_type, check_in, check_out = country_city_room_date
    api_key, admin_username = api_credentials

    # Format the URL with country and city path parameters
    url = f'/api/rooms/?country={country}&city={city}&room={room_type}&check_in={check_in}&check_out={check_out}'

    response = test_client.get(url, headers={
        "Content-Type": "application/json",
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    })

    # Assert the response status code is 200 OK
    assert response.status_code in [200, 409], f"Unexpected status code returned: {response.status_code}"


# test POST create new booking
@pytest.mark.parametrize("customer_id, hotel, room_type, check_in, check_out, payment", [
    (1, "Hotel2", "double", "2024-03-01", "2024-03-05", "credit"),
    (1, "Hotel2", "test", "2025-03-01", "2025-02-01", "credit"),
    (100, "Hotel2", "double", "2025-05-05", "2024-04-04", "credit"),
    (1, "Hotel2", "double", "2025-05-05", "2024-04-04", "credit"),
])
def test_booking_collection_post(test_client, api_credentials, customer_id, hotel, room_type, check_in, check_out, payment):
    api_key, admin_username = api_credentials

    booking_data = {
        "customer_id": customer_id,
        "hotel": hotel,
        "room_type": room_type,
        "check_in": check_in,
        "check_out": check_out,
        "payment": payment
    }

    url = '/api/bookings/'
    response = test_client.post(url, headers={
        "Content-Type": "application/json",
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    }, data=json.dumps(booking_data))

    assert response.status_code in [201, 400, 404], f"Unexpected status code returned: {response.status_code}"
    

# test POST create new booking without hotel
@pytest.mark.parametrize("customer_id, hotel, room_type, check_in, check_out, payment", [
    (1, None, "double", "2024-03-01", "2024-03-05", "credit"),
    # (1, "Hotel2", "test", "2025-03-01", "2025-02-01", "credit"),
    # (100, "Hotel2", "double", "2025-05-05", "2024-04-04", "credit"),
    # (1, "Hotel2", "double", "2025-05-05", "2024-04-04", "credit"),
])
def test_booking_collection_post_no_hotel(test_client, api_credentials, customer_id, hotel, room_type, check_in, check_out, payment):
    api_key, admin_username = api_credentials

    booking_data = {
        "customer_id": customer_id,
        "hotel": hotel,
        "room_type": room_type,
        "check_in": check_in,
        "check_out": check_out,
        "payment": payment
    }

    url = '/api/bookings/'
    response = test_client.post(url, headers={
        "Content-Type": "application/json",
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    }, data=json.dumps(booking_data))

    assert response.status_code in [201, 400, 404], f"Unexpected status code returned: {response.status_code}"
    
# test POST create new booking with out credentials    
@pytest.mark.parametrize("customer_id, hotel, room_type, check_in, check_out, payment", [
    (1, "Hotel2", "double", "2024-03-01", "2024-03-05", "credit"),
])
def test_booking_collection_post_no_apikey_username(test_client, customer_id, hotel, room_type, check_in, check_out, payment):

    booking_data = {
        "customer_id": customer_id,
        "hotel": hotel,
        "room_type": room_type,
        "check_in": check_in,
        "check_out": check_out,
        "payment": payment
    }

    url = '/api/bookings/'
    response = test_client.post(url, headers={
        "Content-Type": "application/json",
    }, data=json.dumps(booking_data))

    assert response.status_code in [400, 404], f"Unexpected status code returned: {response.status_code}"
    
# test POST create new booking with out username    
@pytest.mark.parametrize("customer_id, hotel, room_type, check_in, check_out, payment", [
    (1, "Hotel2", "double", "2024-03-01", "2024-03-05", "credit"),
])
def test_booking_collection_post_no_username(test_client, api_credentials, customer_id, hotel, room_type, check_in, check_out, payment):
    api_key, admin_username = api_credentials
    
    booking_data = {
        "customer_id": customer_id,
        "hotel": hotel,
        "room_type": room_type,
        "check_in": check_in,
        "check_out": check_out,
        "payment": payment
    }

    url = '/api/bookings/'
    response = test_client.post(url, headers={
        "Content-Type": "application/json",
        "Hotels-Api-Key": api_key,
    }, data=json.dumps(booking_data))

    assert response.status_code in [400, 404], f"Unexpected status code returned: {response.status_code}"
    
# test create new booking with out apikey 
@pytest.mark.parametrize("customer_id, hotel, room_type, check_in, check_out, payment", [
    (1, "Hotel2", "double", "2024-03-01", "2024-03-05", "credit"),
])
def test_booking_collection_post_no_apikey(test_client, api_credentials, customer_id, hotel, room_type, check_in, check_out, payment):
    admin_username = api_credentials
    
    booking_data = {
        "customer_id": customer_id,
        "hotel": hotel,
        "room_type": room_type,
        "check_in": check_in,
        "check_out": check_out,
        "payment": payment
    }

    url = '/api/bookings/'
    response = test_client.post(url, headers={
        "Content-Type": "application/json",
        "Hotels-Api-Key": None,
        "Admin-User-Name": admin_username,
    }, data=json.dumps(booking_data))

    assert response.status_code in [400, 403], f"Unexpected status code returned: {response.status_code}"
    
    


@pytest.mark.parametrize("booking_ref", [(1001), (1002), (1003),])
def test_booking_item_get(test_client, api_credentials, booking_ref):
    api_key, admin_username = api_credentials

    url = f'/api/bookings/{booking_ref}/'
    response = test_client.get(url, headers={
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    })

    # Verify the response status code is 200 OK
    assert response.status_code in [200, 403], f"Unexpected status code returned: {response.status_code}"


@pytest.mark.parametrize("booking_ref", [(1001), (1002), (1003), (5000)])
def test_booking_item_delete(test_client, api_credentials, booking_ref):
    api_key, admin_username = api_credentials

    url = f'/api/bookings/{booking_ref}/'
    response = test_client.delete(url, headers={
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    })

    # Verify the booking has been successfully deleted
    assert response.status_code in [204, 403, 404], f"Unexpected status code returned: {response.status_code}"


@pytest.mark.parametrize("booking_ref, customer_id, new_booking_data", [
    (1001, 1, {"customer_id": 2, "hotel": "Hotel2", "room_type": "double", "payment": "credit", "check_in": "2024-03-01","check_out": "2024-03-05"}),
    (1001, 1, {"customer_id": 2, "hotel": "Hotel2", "room_type": "double", "payment": "credit", "check_in": "2024-03-01","check_out": "2024-03-01"}),
    (1003, 2, {"customer_id": 2, "hotel": "Hotel2", "room_type": "single", "payment": "cash", "check_in": "2024-03-05","check_out": "2024-03-10"}), #increase date
    
    (1001, 1, {"customer_id": 2, "hotel": "Hotel1", "room_type": "789", "payment": "credit", "check_in": "2024-03-01","check_out": "2024-03-05"}),
    (1002, 1000, {"customer_id": 1000, "hotel": "Hotel2", "room_type": "double", "payment": "credit", "check_in": "2024-03-01","check_out": "2024-03-05"}),
    (1002, 1000, {"customer_id": 1000, "hotel": "TEST", "room_type": "double", "payment": "credit", "check_in": "2024-03-01","check_out": "2024-03-05"}),
])

def test_booking_item_put(test_client, api_credentials, booking_ref, customer_id, new_booking_data):
    api_key, admin_username = api_credentials

    url = f'/api/bookings/{booking_ref}/'
    response = test_client.put(url, headers={
        "Content-Type": "application/json",
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username,
    }, data=json.dumps(new_booking_data))

    # Check for successful update status code (e.g., 204 No Content or 200 OK if returning updated data)
    assert response.status_code in [204, 403, 404, 400, 409], f"Unexpected status code returned: {response.status_code}"
    

#### HYPER MEDIA TEST#######
"""ChatGPT has been used to generate some of the test functions
for quick testing hypermedia, as the hypermedia test functions are quite similar
in almost every request"""

# Test hypermedia links in the root endpoint
def test_root_endpoint_hypermedia(test_client):
    response = test_client.get('/api/')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    
    #TEST#
    # bookie @naemspace correctness 
    # Assert the presence of the '@namespace' section in the response
    assert "@namespace" in data
    # Assert the presence and correctness of the 'bookie' namespace
    assert "bookie" in data["@namespace"]
    assert "name" in data["@namespace"]["bookie"]
    
    
    #TEST#
    # bookie @controls correctness 
    # Assert the presence of the '@controls' section in the response
    assert "@controls" in data
    # Assert the presence of the 'bookie:add-apikey' control
    assert "bookie:add-apikey" in data["@controls"]
    
    # Assert the presence and correctness of the 'bookie:add-apikey' control's information
    api_control = data["@controls"]["bookie:add-apikey"]
    assert "href" in api_control
    assert "method" in api_control
    assert api_control["method"] == "POST"
    
    #TEST#
    # 'bookie:add-customer' control
    add_customer_control = data["@controls"]["bookie:add-customer"]
    assert "href" in add_customer_control
    assert "method" in add_customer_control
    assert add_customer_control["method"] == "POST"
    
    assert "encoding" in add_customer_control
    assert add_customer_control["encoding"] == "json"
    
    assert "title" in add_customer_control
    assert add_customer_control["title"] == "Add new customer"

    #TEST#
    # Assert the presence and correctness of the schema
    assert "schema" in add_customer_control
    schema = add_customer_control["schema"]
    assert "type" in schema
    assert schema["type"] == "object"
    assert "required" in schema
    assert schema["required"] == ["name", "phone", "mail", "address"]
    assert "properties" in schema
    
    # Assert the presence and correctness of the properties
    properties = schema["properties"]
    assert "name" in properties
    assert "type" in properties["name"]
    assert properties["name"]["type"] == "string"
    assert "phone" in properties
    assert "type" in properties["phone"]


    # Assertions for "bookie:add-apikey" control
    assert "bookie:add-apikey" in data["@controls"]
    add_apikey_control = data["@controls"]["bookie:add-apikey"]
    assert "method" in add_apikey_control
    assert add_apikey_control["method"] == "POST"
    assert "encoding" in add_apikey_control
    assert "title" in add_apikey_control
    assert "schema" in add_apikey_control
    assert "href" in add_apikey_control

    # Assertions for "bookie:delete" control
    assert "bookie:delete" in data["@controls"]
    delete_control = data["@controls"]["bookie:delete"]
    assert "method" in delete_control
    assert delete_control["method"] == "DELETE"
    assert "title" in delete_control
    assert "href" in delete_control

# test for GET customer response
def test_customer_hypermedia(test_client, api_credentials):
    api_key, admin_username = api_credentials
 
    response = test_client.get('/api/customers/1/', headers = {
        "Hotels-Api-Key": api_key, 
        "Admin-User-Name": admin_username
    })

    # Assert the status code of the GET request
    assert response.status_code == 200
    
    # Assert the presence of the customer information in the response
    data = json.loads(response.data)
    assert "item" in data
    assert len(data["item"]) == 1
    customer = data["item"][0]
    assert "id" in customer
    assert "name" in customer
    assert "phone" in customer
    assert "mail" in customer
    assert "address" in customer
    assert "@controls" in customer
    assert "self" in customer["@controls"]
    assert "href" in customer["@controls"]["self"]
    assert customer["@controls"]["self"]["href"] == "/api/customers/1/"

# test for GET room response
def test_rooms_hypermedia(test_client, api_credentials):
    api_key, admin_username = api_credentials
 
    response = test_client.get('/api/rooms/?country=Finland&city=Oulu', headers = {
        "Hotels-Api-Key": api_key, 
        "Admin-User-Name": admin_username
    })

    # Assert the status code of the GET request
    assert response.status_code == 200
    
    # Assert the presence of room information in the response
    data = json.loads(response.data)
    assert "items" in data
    
    # Assert each room item
    for room in data["items"]:
        assert "hotel_name" in room
        assert "hotel_address" in room
        assert "room_type" in room
        assert "price" in room

# Test for GET booking response
def test_booking_hypermedia(test_client, api_credentials):
    api_key, admin_username = api_credentials
 
    response = test_client.get('/api/bookings/1003/', headers = {
        "Hotels-Api-Key": api_key, 
        "Admin-User-Name": admin_username
    })

    # Assert the status code of the GET request
    assert response.status_code == 200
    
    # Assert the presence of booking information in the response
    data = json.loads(response.data)
    assert "item" in data
    assert len(data["item"]) == 1
    booking = data["item"][0]
    assert "booking_ref" in booking
    assert "room_type" in booking
    assert "room_number" in booking
    assert "customer_id" in booking
    assert "check_in" in booking
    assert "check_out" in booking
    assert "payment" in booking
    assert "@controls" in booking
    assert "self" in booking["@controls"]
    assert "href" in booking["@controls"]["self"]
    assert booking["@controls"]["self"]["href"] == "/api/bookings/1003/"
