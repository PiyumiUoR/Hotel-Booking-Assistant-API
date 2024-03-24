import pytest
import requests
BASE_URL = "http://127.0.0.1:5000/"

@pytest.fixture
def api_credentials():
    ADMIN_USERNAME = "heikki"
    ADMIN_PASSWORD = "root"
    api_key = generate_api_key(ADMIN_USERNAME, ADMIN_PASSWORD)  # Renamed function
    yield api_key, ADMIN_USERNAME
    delete_api_key(api_key, ADMIN_USERNAME)  # Renamed function

# Test Case: 1
def generate_api_key(username, password):
    """
    Test case for generating an API key for an admin.
    """
    print("TEST: generate_api_key")
    
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
    
    return api_key

# Test Case: 2
def delete_api_key(api_key, admin_username):
    """
    Test case for deleting an API key for an admin.
    """
    print("TEST: delete_api_key")
    
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

# Test Case: 3
def test_get_customer_information(api_credentials):
    api_key, admin_username = api_credentials  # Unpack the credentials provided by the fixture
    customer_id = 1  # Assuming you have a customer with ID 1
    
    print("TEST: test_get_customer_information")  

    url = f"{BASE_URL}api/customers/{customer_id}/"
    headers = {"Hotels-Api-Key": api_key, "Admin-User-Name": admin_username}

    response = requests.get(url, headers=headers)

    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")

    assert response.status_code in [200, 404, 403], f"Unexpected status code returned: {response.status_code}"

    if response.status_code == 200:
        customer_info = response.json()
        assert all(key in customer_info for key in ['name', 'mail', 'phone', 'address']), "Missing customer information keys"
        print(f"Customer Information:\nName: {customer_info['name']}\nMail: {customer_info['mail']}\nPhone: {customer_info['phone']}\nAddress: {customer_info['address']}")
    elif response.status_code == 403:
        print(f"You don't have permission to view customer information with ID No.{customer_id}")
    else:
        print(f"Unfortunately, the customer you are looking for doesn't exist, or the request was not formatted correctly!")
        
# Test Case: 4
def test_create_customer(api_credentials):
    """
    Test case for creating a new customer using an API key and admin username.
    """
    print("TEST: test_create_customer")  # Print function name
    
    api_key, admin_username = api_credentials
    
    customer_data = {
    "name": "Test Customer",
    "phone": "+3581234567",
    "mail": "test.customer_5@gmail.com",
    "address": "Test Street 1, Test City"
    }
    
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
    
    print("TEST OUTPUTs:")
    if response.status_code == 201:
        print(f"Customer info updated")
    elif response.status_code == 409:
        print(f"E-mail already in use")
    else:
        print(f"Unexpected status code: {response.status_code}")
        
# Test Case: 5
def test_delete_customer(api_credentials):
    print("TEST: test_delete_customer")
    
    api_key, admin_username = api_credentials
    customer_id = 1
    
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
    
    if response.status_code == 204:
        print(f"Customer with ID {customer_id} successfully deleted.")
    elif response.status_code == 405:
        print("DELETE not permitted (Customer has bookings).")
    elif response.status_code == 403:
        print(f"You don't have permission to delete customer with ID No. {customer_id}")
    else:
        print(f"Unexpected status code: {response.status_code}")
        
        
# Test Case: 6
def test_modify_customer(api_credentials):
    print("TEST: test_modify_customer")
    
    api_key, admin_username = api_credentials
    
    customer_id = 1
    
    new_customer_data = {
        "name": "Matti Meikalainen", 
        "address": "Matintie 1",
        "phone": "+358123456789",
        "mail": "testimatti@gmail.com"}
    
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
    
    if response.status_code == 204:
        print(f"Customer with ID {customer_id} successfully updated.")
    elif response.status_code == 409:
        print("Failure in PUT: E-mail already in use.")
    else:
        print(f"Unexpected status code: {response.status_code}")
        
# Test Case: 7
def test_get_available_rooms(api_credentials):
    """
    Test case for getting available rooms.
    """
    print("TEST: test_get_available_rooms()")
    
    api_key, admin_username = api_credentials
    country = "Finland"
    city = "Oulu"
    room_type = "single"
    check_in_date = "2024-03-01"
    check_out_date = "2024-03-05"
    
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
                try:
                    assert "Hotel" in room 
                    print(f"Room available between {check_in_date} - {check_out_date} in {room['Hotel']} - Room {room.get('room', 'N/A')}")
                except AssertionError:
                    print(f"AssertionError: 'Hotel' not found in room:")
                    print(room)
                    raise
    else:
        print(f"No rooms available between {check_in_date} - {check_out_date}")
        
    print("")
    
# Test Case: 8
def test_booking_information(api_credentials):
    """
    Test case for checking booking information using an API key and admin username.
    """
    print("TEST: test_booking_information()")
    api_key, admin_username = api_credentials
    booking_ref = 1001
    
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

    # Check the HTTP status code
    if response.status_code == 404:
        print("TEST OUTPUTs:")
        print(f"Booking with reference {booking_ref} does not exist.")
    elif response.status_code == 403:
        print("TEST OUTPUTs:")
        print("Permission Denied. You don't have permission to access this infomation")
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
        
# Test Case: 9
def test_delete_booking(api_credentials):
    """
    Test case for deleting a booking (existent or non-existent) using an API key and admin username.
    """
    print("TEST: test_delete_booking()")
    api_key, admin_username = api_credentials
    booking_ref = 1003
    
    
    url = f"{BASE_URL}api/bookings/{booking_ref}/"
    
    # Include API key and the Admin-User-Name in the request headers
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.delete(url, headers=headers)

    # Print the request status code
    print("REQUEST STATUS CODE:")
    print(response.request.method, response.request.url)
    
    # Print the response status code and text
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
        
# Test Case: 10
def test_create_booking(api_credentials):
    print("TEST: test_create_booking")
    
    api_key, admin_username = api_credentials
    booking_data = {
    "customer_id": 1,
    "hotel": "Hotel2",
    "room_type": "double",
    "payment": "credit",
    "check_in": "2024-03-01",
    "check_out": "2024-03-05"}
    
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
    
    if response.status_code == 201:
        print("New booking created successfully.")
        booking_location = response.headers.get("Location")
        print(f"Booking Location: {booking_location}")
        return booking_location  # Return the booking location if you need to use it for further actions
    elif response.status_code == 409:
        print("Failure in POST: No room of the requested type is available.")
    else:
        print(f"Unexpected status code: {response.status_code}")

# Test Case: 11
def test_modify_booking(api_credentials):
    print("TEST: test_modify_booking")
    
    api_key, admin_username = api_credentials
    
    booking_ref = 1003
    new_booking_data = {
    "customer_id": 1,
    "hotel": "Hotel2",
    "room_type": "suite",
    "payment": "credit",
    "check_in": "2024-03-01",
    "check_out": "2024-03-05"}
    
    url = f"{BASE_URL}api/bookings/{booking_ref}/"
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username
    }

    response = requests.put(url, json=new_booking_data, headers=headers)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")
    
    if response.status_code == 204:
        print(f"Booking with reference {booking_ref} successfully updated.")
    elif response.status_code == 409:
        print("No rooms corresponding to the criteria are available.")
    else:
        print(f"Unexpected status code: {response.status_code}")