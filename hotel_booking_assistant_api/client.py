import os
import requests
import json
import time
import argparse

API_URL = "http://127.0.0.1:5000"
ISO_DATE = "%Y-%m-%d"
ISO_TIME = "%H:%M:%S"
DATE_FORMATS = ["%Y", ISO_DATE]

class APIError(Exception):
    """
    Exception class used when the API responds with an error code. Gives
    information about the error in the console.
    """

    def __init__(self, code, error):
        """
        Initializes the exception with *code* as the status code from the response
        and *error* as the response body.
        """
    
        self.error = error
        self.code = code
        
    def __str__(self):
        """
        Returns all details from the error response sent by the API formatted into
        a string.
        """

        return "Error {code} while accessing {uri}: {msg}\nDetails:\n{msgs}".format(
            code=self.code,
            uri=self.error["resource_url"],
            msg=self.error["@error"]["@message"],
            msgs="\n".join(self.error["@error"]["@messages"])
        )

def make_iso_format_date(value):
    """
    make_iso_format_date(value) -> string
    
    Tries to create an ISO-8601 date timestamp from the given string by trying
    to parse the original string with different date formats. If unable to parse
    the date automatically, it prompts the conversion from the user.
    """

    for form in DATE_FORMATS:
        try:
            date = time.strptime(value, form)
            value = time.strftime(ISO_DATE, date)
            break
        except ValueError:
            pass
    else:
        value = input("Type ISO format date that matches {}".format(value))
    return value

def get_customer(s, base_resp, id):
    """
    Retrieves customer's details from the API based on the provided customer reference.
    Returns the customer details if found, otherwise raises an APIError.
    """
    base_url = base_resp.json()["@controls"]["bookie:add-customer"]["href"]
    customer_url = f"{base_url}{id}/"

    resp = s.get(API_URL + customer_url)

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 404:
        raise ValueError(f"Customer with reference {id} not found.")
    else:
        raise APIError(resp.status_code, resp.json())
    
def delete_customer(s, base_resp, id):
    """
    Deletes a customer from the API based on the provided customer reference.
    Raises an APIError if the deletion fails.
    """
    base_url = base_resp.json()["@controls"]["bookie:add-customer"]["href"]
    customer_url = f"{base_url}{id}/"

    resp = s.delete(API_URL + customer_url)
    if resp.status_code == 204:
        print(f"Customer with reference {id} deleted successfully.")
    elif resp.status_code == 404:
        raise ValueError(f"Customer with reference {id} not found.")
    else:
        raise APIError(resp.status_code, resp.json())
    
def edit_customer(s, base_resp, id, name, mail, phone, address):
    """
    Edits an existing customer on the API based on the provided customer reference.
    The new data for the customer is provided as keyword arguments.
    Raises an APIError if the edit fails.
    """
    base_url = base_resp.json()["@controls"]["bookie:add-customer"]["href"]
    customer_url = f"{base_url}{id}/"
    resp = s.get(API_URL + customer_url)

    if resp.status_code == 200:
        customer_data = resp.json()

        if "@controls" in customer_data and "edit" in customer_data["@controls"]:
            edit_ctrl = customer_data["@controls"]["edit"]
        
            if "schema" not in edit_ctrl:
                raise KeyError("Schema not found for 'edit' control in edit_booking.")
            
            request_body = generate_request_body_from_schema(
                edit_ctrl["schema"],
                name = name,
                mail = mail,
                phone = phone,
                address = address
            )

            resp = submit_data(s, edit_ctrl, request_body)
            if resp.status_code == 204:
                print(f"Cutomer with reference {id} edited successfully.")
            else:
                raise APIError(resp.status_code)
        else:
            raise KeyError("'edit' control not found in the edit_customer response.")
    else:
        raise ValueError(f"Customer with reference {id} not found.")

def create_customer(s, resp, name, mail, phone, address):
    """
    create_customer(s, name, email, phone, address) -> string
    
    Creates a new customer by sending a POST request to the API with the provided customer details.
    If creation is successful, returns the URI where the customer was placed by the API.
    Otherwise, raises an APIError.
    """    
    body = resp.json()

    # Check if the required control exists
    if "@controls" in body and "bookie:add-customer" in body["@controls"]:
        customer_ctrl = body["@controls"]["bookie:add-customer"]
        if "schema" not in customer_ctrl:
            raise KeyError("Schema not found for 'bookie:add-customer' control.")
        
        request_body = generate_request_body_from_schema(
            customer_ctrl["schema"],
            name = name,
            mail = mail,
            phone = phone,
            address = address
        )

        resp = submit_data(s, customer_ctrl, request_body)
        if resp.status_code == 201:
            customer_id = find_customer_id(resp)
            base_url = body["@controls"]["bookie:add-customer"]["href"]
            customer_url = f"{base_url}{customer_id}/"
            return customer_url
        else: 
            raise APIError(resp.status_code, resp.json())
    else:
        raise KeyError("'bookie:add-customer' control not found in the response.")
    
def find_customer_id(resp):
    """
    Extracts the customer reference from the response object.
    """
    body = resp.json()
    if "item" in body and len(body["item"]) > 0:
        customer_id = body["item"][0]["id"]
        return customer_id
    else:
        raise ValueError("Unable to extract customer ID from the response.")

def get_booking(s, base_resp, booking_ref):
    """
    Retrieves booking details from the API based on the provided booking reference.
    Returns the booking details if found, otherwise raises an APIError.
    """
    base_url = base_resp.json()["@controls"]["bookie:add-booking"]["href"]
    booking_url = f"{base_url}{booking_ref}/"

    resp = s.get(API_URL + booking_url)

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 404:
        raise ValueError(f"Booking with reference {booking_ref} not found.")
    else:
        raise APIError(resp.status_code, resp.json())

def delete_booking(s, base_resp, booking_ref):
    """
    Deletes a booking from the API based on the provided booking reference.
    Raises an APIError if the deletion fails.
    """
    base_url = base_resp.json()["@controls"]["bookie:add-booking"]["href"]
    booking_url = f"{base_url}{booking_ref}/"

    resp = s.delete(API_URL + booking_url)
    if resp.status_code == 204:
        print(f"Booking with reference {booking_ref} deleted successfully.")
    elif resp.status_code == 404:
        raise ValueError(f"Booking with reference {booking_ref} not found.")
    else:
        raise APIError(resp.status_code, resp.json())

def edit_booking(s, base_resp, booking_ref, customer_id, hotel, room_type, payment, check_in, check_out):
    """
    Edits an existing booking on the API based on the provided booking reference.
    The new data for the booking is provided as keyword arguments.
    Raises an APIError if the edit fails.
    """
    base_url = base_resp.json()["@controls"]["bookie:add-booking"]["href"]
    booking_url = f"{base_url}{booking_ref}/"

    resp = s.get(API_URL + booking_url)
    # print("Response:", resp.text)

    if resp.status_code == 200:
        booking_data = resp.json()

        if "@controls" in booking_data and "edit" in booking_data["@controls"]:
            edit_ctrl = booking_data["@controls"]["edit"]
        
            if "schema" not in edit_ctrl:
                raise KeyError("Schema not found for 'edit' control in edit_booking.")
        
            request_body = generate_request_body_from_schema(
                edit_ctrl["schema"],
                customer_id=int(customer_id),
                hotel=hotel,
                room_type=room_type,
                payment=payment,
                check_in=check_in,
                check_out=check_out
            )
        
            resp = submit_data(s, edit_ctrl, request_body)
            if resp.status_code == 204:
                print(f"Booking with reference {booking_ref} edited successfully.")
            else:
                raise APIError(resp.status_code)
        else:
            raise KeyError("'edit' control not found in the edit_booking response.")
    else:
        raise ValueError(f"Booking with reference {booking_ref} not found.")

def create_booking(s, resp, customer_id, hotel, room_type, payment, check_in, check_out):
    """
    Creates a new booking by sending a POST request to the API with the provided booking details.
    If creation is successful, returns the URL of the booking.
    Otherwise, raises an APIError.
    """    
    body = resp.json()
    # print(body)
    
    if "@controls" in body and "bookie:add-booking" in body["@controls"]:
        booking_ctrl = body["@controls"]["bookie:add-booking"]
        
        if "schema" not in booking_ctrl:
            raise KeyError("Schema not found for 'bookie:add-booking' control.")
        
        request_body = generate_request_body_from_schema(
            booking_ctrl["schema"],
            customer_id=int(customer_id),
            hotel=hotel,
            room_type=room_type,
            payment=payment,
            check_in=check_in,
            check_out=check_out
        )
       
        resp = submit_data(s, booking_ctrl, request_body)
        if resp.status_code == 201:
            booking_ref = find_booking_ref(resp)
            base_url = body["@controls"]["bookie:add-booking"]["href"]
            booking_url = f"{base_url}{booking_ref}/"
            # print(booking_url)
            return booking_url
        else: 
            raise APIError(resp.status_code, resp.json())
    else:
        raise KeyError("'bookie:add-booking' control not found in the response.")

def find_booking_ref(resp):
    """
    Extracts the booking reference from the response object.
    """
    body = resp.json()
    if "item" in body and len(body["item"]) > 0:
        booking_ref = body["item"][0]["booking_ref"]
        return booking_ref
    else:
        raise ValueError("Unable to extract booking reference from the response.")

def generate_request_body_from_schema(schema, **kwargs):
    """
    Generates a request body based on the provided schema and keyword arguments.
    """
    request_body = {}
    properties = schema.get("properties", {})
    
    for prop, value in kwargs.items():
        if prop in properties:
            request_body[prop] = value
        else:
            raise ValueError(f"Property '{prop}' not found in schema.")
    
    required_properties = schema.get("required", [])
    for prop in required_properties:
        if prop not in request_body:
            raise ValueError(f"Required property '{prop}' not provided.")
    
    return request_body

def get_rooms(s, rooms_href, country=None, city=None, room_type=None, check_in=None, check_out=None):
    """
    Retrieves available rooms from the API based on the provided query parameters.
    Returns the available rooms if found, otherwise raises an APIError.
    """
    # Define the URL for the RoomCollection endpoint
    rooms_url = API_URL + rooms_href
    
    # Prepare query parameters
    params = {}
    if country:
        params["country"] = country
    if city:
        params["city"] = city
    if room_type:
        params["room_type"] = room_type
    if check_in:
        params["check_in"] = check_in
    if check_out:
        params["check_out"] = check_out
    
    # Send GET request to the API
    resp = s.get(rooms_url, params=params)

    if resp.status_code == 200:
        return resp.json()
    else:
        raise APIError(resp.status_code, resp.json())


def submit_data(s, ctrl, data):
    """
    submit_data(s, ctrl, data) -> requests.Response
    
    Sends *data* provided as a JSON compatible Python data structure to the API
    using URI and HTTP method defined in the *ctrl* dictionary (a Mason @control).
    The data is serialized by this function and sent to the API. Returns the 
    response object provided by requests.
    """
    
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers={"Content-type": "application/json"}
    )
    return resp


# if __name__ == "__main__":
#     with requests.Session() as s:
#         s.headers.update({"Content-Type": "application/vnd.mason+json, */*", "Hotels-Api-Key": "cVjxBovzKlHCNp055FNm5-IG1sjW9xu_WGH22CbDE3w", "Admin-User-Name": "aino"})
#         resp = s.get(API_URL + "/api/")
#         if resp.status_code != 200:
#             print("Unable to access API.")
#         else:
#             body = resp.json()
#             rooms_href = body["@controls"]["bookie:rooms-av-all"]["href"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for interacting with the API")
    parser.add_argument("action", choices=["create_customer", "create_booking", "edit_customer", "edit_booking", "delete_customer", "delete_booking", "get_customer", "get_booking", "get_rooms"], help="Action to perform (create_customer, create_booking, edit_customer, edit_booking, delete_customer, delete_booking, get_customer, get_booking)")
    parser.add_argument("--username", required=True, help="Username for authentication")
    parser.add_argument("--api_key", required=True, help="API key for authentication")
    parser.add_argument("--customer_id", help="Customer or booking ID")
    parser.add_argument("--name", help="Customer name")
    parser.add_argument("--mail", help="Customer email")
    parser.add_argument("--phone", help="Customer phone")
    parser.add_argument("--address", help="Customer address")
    parser.add_argument("--hotel", help="Hotel name")
    parser.add_argument("--country", help="Country of the hotel(starts from capital letter)")
    parser.add_argument("--city", help="City of the hotel(starts from capital letter)")
    parser.add_argument("--room_type", help="Room type")
    parser.add_argument("--payment", help="Payment method")
    parser.add_argument("--check_in", help="Check-in date")
    parser.add_argument("--check_out", help="Check-out date")
    parser.add_argument("--booking_ref", help="Booking reference")
    args = parser.parse_args()

    headers = {
        "Content-Type": "application/vnd.mason+json, */*",
        "Hotels-Api-Key": args.api_key,
        "Admin-User-Name": args.username
    }

    with requests.Session() as s:
        s.headers.update(headers)
        resp = s.get(API_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            rooms_href = body["@controls"]["bookie:rooms-av-all"]["href"]

            if args.action == "create_customer":
                create_customer(s, resp, args.name, args.mail, args.phone, args.address)
            elif args.action == "create_booking":
                create_booking(s, resp, args.customer_id, args.hotel, args.room_type, args.payment, args.check_in, args.check_out)
            elif args.action == "edit_customer":
                edit_customer(s, resp, args.customer_id, args.name, args.mail, args.phone, args.address)
            elif args.action == "edit_booking":
                edit_booking(s, resp, args.booking_ref, args.customer_id, args.hotel, args.room_type, args.payment, args.check_in, args.check_out)
            elif args.action == "delete_customer":
                delete_customer(s, resp, args.customer_id)
            elif args.action == "delete_booking":
                delete_booking(s, resp, args.booking_ref)
            elif args.action == "get_customer":
                get_customer(s, resp, args.customer_id)
            elif args.action == "get_booking":
                get_booking(s, resp, args.booking_ref)
            elif args.action == "get_rooms":
                get_rooms(s, rooms_href)
