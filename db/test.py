import requests
from json.decoder import JSONDecodeError
BASE_URL = "http://127.0.0.1:5000/"

# WORKS

def test_get_customer_information(customer_id): #valid input for customer_id 1-3
    """
    Test case for getting customer information.
    """
    print("TEST: test_get_customer_information") # print function name
    
    url = f"{BASE_URL}/api/customers/{customer_id}/"

    response = requests.get(url)
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")

    # Check the HTTP status code
    assert response.status_code in [200, 404]

    print("TEST OUTPUTs:")
    if response.status_code == 200:
        customer_info = response.json()
        print(f"Customer Information:\nName: {customer_info['name']}\nMail: {customer_info['mail']}\nAddress: {customer_info['address']}")
    else:
        print(f"Unfortunately, the customer you are looking for doesn't exist or the customer did not make any reservation yet!")
        
    print("")



def test_get_available_rooms(country, city, room_type, check_in_date, check_out_date):
    """
    Test case for getting available rooms.
    """
    print("TEST: test_get_available_rooms()")
    
    url = f"{BASE_URL}/api/hotels/{country}/{city}/rooms/"
    # url = f"{BASE_URL}/api/rooms/{country}/{city}/"
    params = {
        "room": room_type,
        "check_in": check_in_date,
        "check_out": check_out_date
    }

    response = requests.get(url, params=params)
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
    
        
        
def test_booking_information(booking_ref):
    """
    Test case for checking booking information
    """
    print("TEST: test_booking_information()")
    
    url = f"{BASE_URL}/api/bookings/{booking_ref}/"


    response = requests.get(url)
    
    print("STATUS PRINTs:")
    print(response.status_code)
    print(response.text)
    print("")

    # Check the HTTP status code for the GET request
    if response.status_code == 404:
        print("TEST OUTPUTs:")
        print(f"Booking with reference {booking_ref} does not exist.")
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
        
        
def test_delete_booking(booking_ref):
    """
    Test case for deleting a nonexistent booking.
    """
    print("TEST: test_delete_booking()")
    
    # nonexistent_booking_ref = "abc123"
    # booking_ref = "1001"
    url = f"{BASE_URL}/api/bookings/{booking_ref}/"

    # Perform the DELETE request
    response = requests.delete(url)

    # Print the request status code
    print("REQUEST STATUS CODE:")
    print(response.request.method, response.request.url, response.request.headers.get("status"))
    
    # Print the response status code
    print("")
    print("RESPONSE STATUS CODE:")
    print(response.status_code)
    print(response.text)
    print("")

    print("TEST OUTPUTs:")
    print(f"Delete booking with reference: {booking_ref}")
    
    if response.status_code == 204:
        print(f"Booking with reference {booking_ref} successfully deleted (Status Code: 204)")
    elif response.status_code == 404:
        print(f"booking reference {booking_ref} does not exist. Attempted to delete booking with reference {booking_ref} was unsuccessful.")
    else:
        print(f"Unexpected status code: {response.status_code}")


def test_get_nonexistent_booking(nonexistent_booking_ref):
    """
    Test case for getting information about a nonexistent booking.
    """
    print("TEST: test_get_nonexistent_booking")
    
    # nonexistent_booking_ref = "abc123"
    url = f"{BASE_URL}/api/bookings/{nonexistent_booking_ref}/"

    
    # Print the response status code
    response = requests.get(url)
    print("")
    print("RESPONSE STATUS CODE:")
    print(response.status_code)
    print(response.text)
    print("")

    print("TEST OUTPUTs:")
    if response.status_code == 404:
        print(f"{nonexistent_booking_ref} does not exist.")
    else:
        print(f"booking reference {nonexistent_booking_ref} does exist.")



def test_create_customer(customer_data):
    """
    Test case for creating a new customer.
    """
    print("TEST: test_create_customer()")
    url = BASE_URL + "/api/customers/"

    # Send a POST request to create a new customer
    response = requests.post(url, json=customer_data)

    # test_create_customer(customer_data = {
    # "name": "NewCustomer",
    # "phone": "+358123554",
    # "mail": "NewCustomer@gmail.com",
    # "address": "yliopistokatu 5, Oulu"
    # })
    
    # Print the status code of the response
    print("")
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
        
    # try:
    #     # Get the response data as JSON
    #     response_data = response.json()
    #     print("Response Data:", response_data)
    # except JSONDecodeError as e:
    #     print("Failed to decode response JSON:", e)

    # Print the location header
    location_header = response.headers.get("Location")
    if location_header:
        print("Location Header:", location_header)
    else:
        print("Location Header not found")



# test_get_customer_information(6) # testing with valid input 1 - 3 
# test_get_customer_information(4) # testing with invalid input

# test_get_available_rooms("Finland", "Oulu", "single", "2024-03-01", "2024-03-05") # testing with valid input
# test_get_available_rooms("USA", "New York", "single", "2024-03-01", "2024-03-05") # testing with invalid input

# test_booking_information(1003) # testing with valid input 1001 - 1004
# test_booking_information(1005) # testing with invalid input

# test_delete_booking(1003) # valid input 1001 - 1004 
# test_delete_booking(1005) # testing with valid input

# test_get_nonexistent_booking(1005)


test_create_customer(customer_data = {
    "name": "NewCustomer",
    "phone": "+358123554",
    "mail": "NewCustomer@gmail.com",
    "address": "yliopistokatu 5, Oulu"
})




# ----------------
