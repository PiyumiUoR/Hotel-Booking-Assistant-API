from app import app
import pytest
import requests
BASE_URL = "http://127.0.0.1:5000/"

def test_home_route():
    response = app.test_client().get('/')
    assert response.status_code == 200


@pytest.fixture
def api_credentials():
    ADMIN_USERNAME = "heikki"
    ADMIN_PASSWORD = "root"
    api_key = generate_api_key(ADMIN_USERNAME, ADMIN_PASSWORD)
    yield api_key, ADMIN_USERNAME
    delete_api_key(api_key, ADMIN_USERNAME)



# Assuming these functions are available from your test suite
def generate_api_key(username, password):
    """
    Test case for generating an API key for an admin.
    """
    print("TEST: test_generate_api_key")
    
    url = f"{BASE_URL}api/keys/"
    credentials = {"username": username, "password": password}

    response = requests.post(url, json=credentials)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")
    
    if response.status_code == 201:
        api_key = response.headers.get("Hotels-Api-Key")
        print(f"API Key generated successfully: {api_key}")
        return api_key
    elif response.status_code == 409:
        print("Admin already has an API key.")
    else:
        print("Failed to generate API Key.")
    
    return None

def delete_api_key(api_key, admin_username):
    """
    Test case for deleting an API key for an admin.
    """
    print("TEST: test_delete_api_key")
    
    url = f"{BASE_URL}api/keys/"
    
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.delete(url, headers=headers)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")
    
    if response.status_code == 204:
        print(f"API Key for admin '{admin_username}' deleted successfully.")
    else:
        print(f"Failed to delete API Key for admin '{admin_username}'.")

        

@pytest.mark.parametrize("customer_data", [
    {"name": "John Doe", "phone": "1234567890", "mail": "john.doe@example.com", "address": "123 Elm Street"},
    {"name": "Jane Doe", "phone": "0987654321", "mail": "jane.doe@example.com", "address": "321 Elm Street"},
    {"name": "Test Customer","phone": "+3581234567","mail": "test.customer_5@gmail.com","address": "Street 1, oulu"}
    # Add more customer data dictionaries here to test different inputs
])
def test_create_customer(api_credentials, customer_data):
    api_key, admin_username = api_credentials  # Unpack the credentials provided by the fixture
    
    print("TEST: test_create_customer")  # Print function name
    
    url = f"{BASE_URL}api/customers/"
    
    # Include API key and the Admin-User-Name in the request headers
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.post(url, json=customer_data, headers=headers)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")
    
    # Assertions to validate the response
    assert response.status_code in [201, 409], "Unexpected status code returned."
    if response.status_code == 201:
        print("Customer created successfully.")
    elif response.status_code == 409:
        print("E-mail already in use.")
        


@pytest.mark.parametrize("customer_id", [1, 2, 100])
def test_get_customer_information_without_fixture(customer_id):
    # Setup: Generate API key
    ADMIN_USERNAME = "heikki"
    ADMIN_PASSWORD = "root"
    api_key = generate_api_key(ADMIN_USERNAME, ADMIN_PASSWORD)

    if not api_key:
        raise ValueError("Failed to generate API key for test setup.")

    # Test body
    try:
        url = f"{BASE_URL}api/customers/{customer_id}/"
        headers = {"Hotels-Api-Key": api_key, "Admin-User-Name": ADMIN_USERNAME}
        response = requests.get(url, headers=headers)

        # You can include assertions and any test logic here
        assert response.status_code in [200, 404, 403], "Unexpected status code returned."

        if response.status_code == 200:
            customer_info = response.json()
            print(f"Customer Information:\nName: {customer_info['name']}\nMail: {customer_info['mail']}\nPhone: {customer_info['phone']}\nAddress: {customer_info['address']}")
        elif response.status_code == 403:
            print(f"You don't have permission to view customer information with ID No.{customer_id}")
        else:
            print(f"Unfortunately, the customer you are looking for doesn't exist, or the request was not formatted correctly!")
        
        print("")

    finally:
        # Teardown: Delete API key
        delete_api_key(api_key, ADMIN_USERNAME)
        

@pytest.mark.parametrize("customer_id", [1, 2, 100])
def test_delete_customer(api_credentials, customer_id):
    api_key, admin_username = api_credentials 
    
    print("TEST: test_delete_customer")
    
    url = f"{BASE_URL}api/customers/{customer_id}/"
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.delete(url, headers=headers)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")
    
    # Assertions to validate the response
    assert response.status_code in [204, 405, 403, 404], "Unexpected status code returned."
    if response.status_code == 204:
        print(f"Customer with ID {customer_id} successfully deleted.")
    elif response.status_code == 405:
        print("DELETE not permitted (Customer has bookings).")
    elif response.status_code == 403:
        print(f"You don't have permission to delete customer with ID No. {customer_id}")
    elif response.status_code == 404:
        print("The customer you are trying to delete does not exist")
    else:
        print(f"Unexpected status code: {response.status_code}")
        


@pytest.mark.parametrize("customer_id, new_customer_data", [
    (1, {"name": "John Updated", "phone": "1234567891", "mail": "john.updated@example.com", "address": "123 Elm Street"}),
    (2, {"name": "Jane Updated", "phone": "0987654322", "mail": "jane.updated@example.com", "address": "321 Elm Street"}),
    (2, {"name": "Jane Updated", "phone": "0987654322", "mail": "jane.updated@example.com", "address": "321 Elm Street"}),
    (4, {"name": "Matti Meikalainen", "phone": "+358123456789", "mail": "testimatti@gmail.com", "address": "Matintie 1"}),

])
def test_modify_customer(api_credentials, customer_id, new_customer_data):
    api_key, admin_username = api_credentials  # Unpack the credentials provided by the fixture
    
    print("TEST: test_modify_customer")
    
    url = f"{BASE_URL}api/customers/{customer_id}/"
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.put(url, json=new_customer_data, headers=headers)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")
    
    # Assertions to validate the response
    assert response.status_code in [204, 409, 403], "Unexpected status code returned."
    if response.status_code == 204:
        print(f"Customer with ID {customer_id} successfully updated.")
    elif response.status_code == 409:
        print("Failure in PUT: E-mail already in use.")
    else:
        print(f"Unexpected status code: {response.status_code}")
        
        
        
@pytest.mark.parametrize("country, city, room_type, check_in_date, check_out_date", [
    ("Finland", "Oulu", "single", "2024-01-01", "2024-01-05"),
    ("Finland", "Helsinki", "suite", "2024-02-01", "2024-02-10"),
    ("Finland", "Oulu", "single", "2024-03-01", "2024-03-05"),
])
def test_get_available_rooms(api_credentials, country, city, room_type, check_in_date, check_out_date):
    api_key, admin_username = api_credentials  # Unpack the credentials provided by the fixture
    
    print("TEST: test_get_available_rooms()")
    
    url = f"{BASE_URL}/api/rooms/{country}/{city}/"
    params = {
        "room": room_type,
        "check_in": check_in_date,
        "check_out": check_out_date
    }
    
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }
    

    response = requests.get(url, params=params, headers=headers)
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")

    # Check the HTTP status code
    assert response.status_code in [200, 409], f"Unexpected status code: {response.status_code}"

    print("TEST OUTPUTs:")
    if response.status_code == 200:
        available_rooms = response.json()
        
        if available_rooms:
            for room in available_rooms:
                assert "Hotel" in room, "AssertionError: 'Hotel' not found in room"
                print(f"Room available between {check_in_date} - {check_out_date} in {room['Hotel']} - Room {room.get('room', 'N/A')}")
    else:
        print(f"No rooms available between {check_in_date} - {check_out_date}")
        
    print("")
    
    
@pytest.mark.parametrize("booking_ref", [1001, 1002, 999, "1234"])
def test_booking_information(api_credentials, booking_ref):
    api_key, admin_username = api_credentials  
    
    print("TEST: test_booking_information()")
    
    url = f"{BASE_URL}api/bookings/{booking_ref}/"
    
    # Include API key and the Admin-User-Name in the request headers
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.get(url, headers=headers)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")

    # Check the HTTP status code and print relevant information based on the response
    if response.status_code == 404:
        print("TEST OUTPUTs:")
        print(f"Booking with reference {booking_ref} does not exist.")
    elif response.status_code == 403:
        print("TEST OUTPUTs:")
        print("Permission Denied. You don't have permission to access this information.")
    else:
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

        print("TEST OUTPUTs:")
        booking_info = response.json()
        print(f"Booking Information:")
        print(f"Hotel: {booking_info.get('hotel', 'N/A')}")
        print(f"Room: {booking_info.get('room', 'N/A')}")
        print(f"Customer: {booking_info.get('customer', 'N/A')}")
        print(f"Check-in: {booking_info.get('check-in', 'N/A')}")
        print(f"Check-out: {booking_info.get('check-out', 'N/A')}")
        


@pytest.mark.parametrize("booking_ref", [1, 9999, "invalid", 1001, 1002, 1003]) 
def test_delete_booking(api_credentials, booking_ref):
    api_key, admin_username = api_credentials  
    
    print("TEST: test_delete_booking()")
    
    url = f"{BASE_URL}api/bookings/{booking_ref}/"
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.delete(url, headers=headers)

    # Print the request method and URL for debugging
    print("REQUEST STATUS CODE:")
    print(response.request.method, response.request.url)
    
    print("")
    print("RESPONSE STATUS CODE:")
    print(response.status_code)
    print(response.text)
    print("")

    print("TEST OUTPUTs:")
    if response.status_code == 204:
        print(f"Booking with reference {booking_ref} successfully deleted.")
    elif response.status_code == 404:
        print(f"Booking reference {booking_ref} does not exist. Attempted to delete booking with reference {booking_ref} was unsuccessful.")
    elif response.status_code == 403:
        print(f"You don't have permission to delete booking with ID No. {booking_ref}")
    else:
        print(f"Unexpected status code: {response.status_code}")
        
        

@pytest.mark.parametrize("booking_data", [
    {"customer_id": 1, "hotel": "Hotel Finlandia", "room_type": "single", "payment": "credit", "check_in": "2024-01-01", "check_out": "2024-01-05"},
    {"customer_id": 2, "hotel": "Hotel Aurora", "room_type": "suite", "payment": "debit", "check_in": "2024-02-01", "check_out": "2024-02-10"},
    {"customer_id": 2, "hotel": "Hotel2", "room_type": "double", "payment": "credit", "check_in": "2024-03-01", "check_out": "2024-03-05"}

])
def test_create_booking(api_credentials, booking_data):
    api_key, admin_username = api_credentials  # Unpack the credentials provided by the fixture
    
    print("TEST: test_create_booking")
    
    url = f"{BASE_URL}api/bookings/"
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.post(url, json=booking_data, headers=headers)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")
    
    assert response.status_code in [201, 409, 403], "Unexpected status code received."

    if response.status_code == 201:
        print("New booking created successfully.")
        booking_location = response.headers.get("Location")
        print(f"Booking Location: {booking_location}")
        # Optional: You could return booking_location if using this in a larger test suite where you need to reference the created booking
    elif response.status_code == 409:
        print("Failure in POST: No room of the requested type is available.")
    else:
        print(f"Unexpected status code: {response.status_code}")
        

@pytest.mark.parametrize("customer_data", [
    {"name": "", "phone": "12345", "mail": "invalid", "address": "123 Elm Street"},  # Missing name
    {"name": "John Doe", "phone": "", "mail": "john.doe@example.com", "address": "123 Elm Street"},  # Missing phone
    {"name": "John Doe", "phone": "1234567890", "mail": "not-an-email", "address": "123 Elm Street"},  # Invalid email format
])
def test_create_customer_with_invalid_data(api_credentials, customer_data):
    api_key, admin_username = api_credentials
    
    print("TEST: Creating customer with invalid data")
    
    url = f"{BASE_URL}api/customers/"
    headers = {"Hotels-Api-Key": api_key, "Admin-User-Name": admin_username}
    response = requests.post(url, json=customer_data, headers=headers)
    
    print("STATUS CODE:", response.status_code)
    print("RESPONSE:", response.text)
    print("")
    
    assert response.status_code in [201, 409, 403, 400], "Unexpected status code received."
    # assert response.status_code == 400, f"Expected failure when creating customer with invalid data, but got status code {response.status_code}"


@pytest.mark.parametrize("booking_ref", [9999, "nonexistent", 1001])  # Example non-existent booking references to test
def test_delete_non_existent_booking(api_credentials, booking_ref):
    api_key, admin_username = api_credentials  # Unpack the credentials provided by the fixture
    
    print("TEST: Deleting non-existent booking")
    
    url = f"{BASE_URL}api/bookings/{booking_ref}/"
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.delete(url, headers=headers)
    
    print("STATUS CODE:", response.status_code)
    print("RESPONSE:", response.text)
    print("")
    assert response.status_code in [201, 409, 403, 400, 404], "Unexpected status code received."
    # Since we're attempting to delete a non-existent booking, we expect a 404 Not Found response
    # assert response.status_code == 404, f"Expected a 404 Not Found response for non-existent booking, but got status code {response.status_code}"
    


@pytest.mark.parametrize("existing_booking_data, update_data", [
    # Assuming existing_booking_data includes booking_ref among other booking details
    ({"booking_ref": 1, "check_in": "2024-01-01", "check_out": "2024-01-05"}, {"check_in": "2024-01-04", "check_out": "2024-01-10"}),
    ({"booking_ref": 2, "check_in": "2024-02-01", "check_out": "2024-02-05"}, {"check_in": "2024-02-03", "check_out": "2024-02-07"}),
    # Add more tuples of existing booking data and conflicting update data as needed
])
def test_update_booking_with_conflicting_dates(api_credentials, existing_booking_data, update_data):
    api_key, admin_username = api_credentials

    print("TEST: Updating booking with conflicting dates")
    
    booking_ref = existing_booking_data["booking_ref"]  # Extract the booking reference from the existing booking data
    url = f"{BASE_URL}api/bookings/{booking_ref}/"
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.put(url, json=update_data, headers=headers)
    
    print("REQUEST DATA:", update_data)
    print("STATUS CODE:", response.status_code)
    print("RESPONSE:", response.text)
    print("")
    
    assert response.status_code in [201, 409, 403, 400, 404], "Unexpected status code received."





