from flask import Blueprint, jsonify, request, flash
from backend import Backend
import logging

logging.basicConfig(level=logging.DEBUG, filename="api.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

api = Blueprint("api", __name__)

global backend_connection
backend_connection = Backend(database="PERSONAL")

@api.route("/check-login-details", methods = ["POST"])
def check_login_details():
    correct = backend_connection.check_password(email=request.get_json()["email"], password_attempt=request.get_json()["password"])

    return jsonify({
        "correct": correct[0],
        "userID": correct[1],
        "userType": correct[2]
    })

@api.route("/create-account", methods = ["POST"])
def create_account():
    request_dict = request.get_json()

    logging.debug(f"{request_dict = }")

    if request_dict["fName"] == "" or request_dict["email"] == "" or request_dict["phone"] == "" or request_dict["password"] == "":
        return jsonify({
            "code": 401,
            "message": "Not all fields filled in."
        })
    
    if not request_dict["phone"].replace(" ", "").isnumeric(): # Checks phone is valid
        return jsonify({
            "code": 401,
            "message": "Invalid phone number given."
        })

    if len(request_dict["email"].split("@")) != 2:
        return jsonify({
            "code": 401,
            "message": "Invalid email format."
        })
    
    if len((request_dict["email"].split("@"))[1].split(".")) < 2:#
        return jsonify({
            "code": 401,
            "message": "Invalid email format."
        })
    
    if request_dict["password"] != request_dict["repeatPassword"]:
        return jsonify({
            "code": 401,
            "message": "Password do not match."
        })
    
    backend_connection.create_user(request_dict["fName"], request_dict["lName"], request_dict["email"], request_dict["phone"], request_dict["password"])

    return jsonify({
        "code": 200
    })

@api.route("/add-event", methods = ["POST"])
def add_event():
    logging.debug("API Add Event Triggered")
    request_dict = request.get_json()

    request_dict["childPrice"] = float(request_dict["childPrice"])
    request_dict["adultPrice"] = float(request_dict["adultPrice"])
    request_dict["elderlyPrice"] = float(request_dict["elderlyPrice"])

    logging.debug(f"{request_dict = }")

    #TODO: validation

    performance_id = backend_connection.add_performance(request_dict["title"], request_dict["description"], request_dict["childPrice"], request_dict["adultPrice"], request_dict["elderlyPrice"])
    
    for seat in request_dict["unavailableSeats"]:
        backend_connection.mark_seat_unavailable(seat, performance_id)

    return jsonify({
        "code": 200
    })