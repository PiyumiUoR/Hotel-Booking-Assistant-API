import pytest
import requests

BASE_URL = "http://127.0.0.1:5000/"

#pronlems: cant get new customer info after creating one because dont have correct permission
def test_get_customer_information(customer_id, api_key, admin_username):
    """
    Test case for getting customer information using an API key and admin username.
    """
    print("TEST: test_get_customer_information")  


    url = f"{BASE_URL}api/customers/{customer_id}/"
    
    # Include API key and the Admin-User-Name in the request headers
    headers = {
        "Hotels-Api-Key": api_key,
        "Admin-User-Name": admin_username 
    }

    # Make the GET request with headers
    response = requests.get(url, headers=headers)

    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")

    # Check the HTTP status code 
    assert response.status_code in [200, 404, 403], "Unexpected status code returned."

    if response.status_code == 200:
        customer_info = response.json()
        print(f"Customer Information:\nName: {customer_info['name']}\nMail: {customer_info['mail']}\nPhone: {customer_info['phone']}\nAddress: {customer_info['address']}")
    elif response.status_code == 403:
        print(f"You don't have permission to view customer information with ID No.{customer_id}")
    else:
        print(f"Unfortunately, the customer you are looking for doesn't exist, or the request was not formatted correctly!")
    
    print("")
    
    

def test_create_customer(customer_data, api_key, admin_username):
    """
    Test case for creating a new customer using an API key and admin username.
    """
    
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
    
    print("TEST OUTPUTs:")
    if response.status_code == 201:
        print(f"Customer info updated")
    elif response.status_code == 409:
        print(f"E-mail already in use")
    else:
        print(f"Unexpected status code: {response.status_code}")

#problems: cant delete because customer hv bookings
def test_delete_customer(customer_id, api_key, admin_username):
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
    
    if response.status_code == 204:
        print(f"Customer with ID {customer_id} successfully deleted.")
    elif response.status_code == 405:
        print("DELETE not permitted (Customer has bookings).")
    elif response.status_code == 403:
        print(f"You don't have permission to delete customer with ID No. {customer_id}")
    else:
        print(f"Unexpected status code: {response.status_code}")


def test_modify_customer(customer_id, new_customer_data, api_key, admin_username):
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
    
    if response.status_code == 204:
        print(f"Customer with ID {customer_id} successfully updated.")
    elif response.status_code == 409:
        print("Failure in PUT: E-mail already in use.")
    else:
        print(f"Unexpected status code: {response.status_code}")


def test_get_available_rooms(country, city, room_type, check_in_date, check_out_date, api_key, admin_username):
    """
    Test case for getting available rooms.
    """
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
    

def test_booking_information(booking_ref, api_key, admin_username):
    """
    Test case for checking booking information using an API key and admin username.
    """
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


# problem dont hv permision to delete booking
def test_delete_booking(booking_ref, api_key, admin_username):
    """
    Test case for deleting a booking (existent or non-existent) using an API key and admin username.
    """
    print("TEST: test_delete_booking()")
    
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


def test_create_booking(booking_data, api_key, admin_username):
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
    
    if response.status_code == 201:
        print("New booking created successfully.")
        booking_location = response.headers.get("Location")
        print(f"Booking Location: {booking_location}")
        return booking_location  # Return the booking location if you need to use it for further actions
    elif response.status_code == 409:
        print("Failure in POST: No room of the requested type is available.")
    else:
        print(f"Unexpected status code: {response.status_code}")


def test_modify_booking(booking_ref, new_booking_data, api_key, admin_username):
    print("TEST: test_modify_booking")
    
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




def test_generate_api_key(username, password):
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

def test_delete_api_key(api_key, admin_username):
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



'''
FUNCTION CALLS
'''

ADMIN_USERNAME = "heikki"
ADMIN_PASSWORD = "root"
api_key = test_generate_api_key(ADMIN_USERNAME, ADMIN_PASSWORD)


if api_key:
    # print("")
    # test_get_customer_information(1, api_key, ADMIN_USERNAME) 
    
    # print("")
    # test_create_customer(customer_data = {
    # "name": "Test Customer",
    # "phone": "+3581234567",
    # "mail": "test.customer_5@gmail.com",
    # "address": "Test Street 1, Test City"
    # }, api_key=api_key, admin_username=ADMIN_USERNAME)
    
    # print("")
    # test_delete_customer(1, api_key, ADMIN_USERNAME)
    
    # print("")
    # test_modify_customer(4, 
    #     new_customer_data = {
    #     "name": "Matti Meikalainen", 
    #     "address": "Matintie 1",
    #     "phone": "+358123456789",
    #     "mail": "testimatti@gmail.com"},
    #     api_key=api_key, admin_username=ADMIN_USERNAME)
    
    # print("")
    # test_get_available_rooms("Finland", "Oulu", "single", "2024-03-01", "2024-03-05", api_key, ADMIN_USERNAME)
    
    # print("")
    # test_booking_information(1003, api_key, ADMIN_USERNAME) # testing with existing booking ID and corect access right
    
    # print("")
    # test_booking_information(1001, api_key, ADMIN_USERNAME) # testing with existing booking ID and wrong access right
    
    # print("")
    # test_booking_information(5000, api_key, ADMIN_USERNAME) # testing with nonexisting booking
    
    # print("")
    # test_delete_booking(1003, api_key, ADMIN_USERNAME) # Test deleting booking with correct permission
    # test_delete_booking(1001, api_key, ADMIN_USERNAME) # Test deleting bookig with wrong permission
    
    # print("")
    # test_create_booking(booking_data = {
    # "customer_id": 1,
    # "hotel": "Hotel2",
    # "room_type": "double",
    # "payment": "credit",
    # "check_in": "2024-03-01",
    # "check_out": "2024-03-05"},api_key=api_key, admin_username=ADMIN_USERNAME)
    
    print("")
    test_modify_booking(1003, new_booking_data = {
    "customer_id": 2,
    "hotel": "Hotel2",
    "room_type": "double",
    "payment": "credit",
    "check_in": "2024-03-01",
    "check_out": "2024-03-05"},api_key=api_key, admin_username=ADMIN_USERNAME)
    
    print("")
    api_key = test_delete_api_key(api_key, ADMIN_USERNAME)
    print(api_key)
else:
    print("Cannot proceed with the test without an API key.")





'''
My TEST CODEs:    
''' 

# def test_generate_api_key(username, password):
#     """
#     Test case for generating an API key for an admin.
#     """
#     print("TEST: test_generate_api_key")
    
#     url = f"{BASE_URL}api/keys/"
#     credentials = {"username": username, "password": password}

#     response = requests.post(url, json=credentials)
    
#     print("STATUS PRINTs:")
#     print(response.status_code)
#     print(response.text)
#     print("")
    
#     if response.status_code == 201:
#         api_key = response.headers.get("Hotels-Api-Key")
#         print(f"API Key generated successfully: {api_key}")
#         return api_key
#     elif response.status_code == 409:
#         print("Admin already has an API key.")
#     else:
#         print("Failed to generate API Key.")
    
#     return None


# def test_delete_api_key(api_key, admin_username):
#     """
#     Test case for deleting an API key for an admin.
#     """
#     print("TEST: test_delete_api_key")
    
#     url = f"{BASE_URL}api/keys/"
#     headers = {
#         "Hotels-Api-Key": api_key,
#         "Admin-User-Name": admin_username
#     }

#     response = requests.delete(url, headers=headers)
    
#     print("STATUS PRINTs:")
#     print(response.status_code)
#     print(response.text)
#     print("")
    
#     if response.status_code == 204:
#         print(f"API Key for admin '{admin_username}' deleted successfully.")
#     else:
#         print(f"Failed to delete API Key for admin '{admin_username}'.")


# ADMIN_USERNAME = "aino"
# ADMIN_PASSWORD = "root"

# api_key = test_generate_api_key(ADMIN_USERNAME, ADMIN_PASSWORD)

# print(api_key)
# test_delete_api_key(api_key, ADMIN_USERNAME)
# api_key = None
# print(api_key)


    
    