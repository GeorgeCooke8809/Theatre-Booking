from flask import Blueprint, jsonify, request, flash
from backend import Backend
import logging
from datetime import datetime

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

    logging.debug(f"{request_dict = }")

    if len(request_dict["title"]) == 0:
        return jsonify({
            "code": 401,
            "message": "You performance does not have a title."
        })
    
    if len(request_dict["title"]) > 100:
        return jsonify({
            "code": 401,
            "message": "Your title is too long. Please limit it to 100 characters."
        })
    
    try:
        request_dict["childPrice"] = float(request_dict["childPrice"])
        request_dict["adultPrice"] = float(request_dict["adultPrice"])
        request_dict["elderlyPrice"] = float(request_dict["elderlyPrice"])
    except ValueError: # Triggered when cannot convert one of the prices
        return jsonify({
            "code": 401,
            "message": "One of your prices is not a number."
        })

    if request_dict["childPrice"] >= 100_000 or request_dict["adultPrice"] >= 100_000 or request_dict["elderlyPrice"] >= 100_000:
        return jsonify({
            "code": 401,
            "message": "One or more of your prices are too high."
        })
        
    child_split = str(request_dict["childPrice"]).split(".")
    adult_split = str(request_dict["adultPrice"]).split(".")
    elderly_split = str(request_dict["adultPrice"]).split(".")

    if len(child_split) == 2:
        if len(child_split[1]) > 2:
            return jsonify({
                "code": 401,
                "message": "Your child price has too many decimal places."
            })
        
    if len(adult_split) == 2:
        if len(adult_split[1]) > 2:
            return jsonify({
                "code": 401,
                "message": "Your adult price has too many decimal places."
            })
        
    if len(elderly_split) == 2:
        if len(elderly_split[1]) > 2:
            return jsonify({
                "code": 401,
                "message": "Your elderly price has too many decimal places."
            })

    for seat in request_dict["unavailableSeats"]:
        if backend_connection._check_valid_seat_ID(seat) == False:
            return jsonify({
                "code": 401,
                "message": "There was an invalid seat in your request."
            })

    performance_id = backend_connection.add_performance(request_dict["title"], request_dict["description"], request_dict["childPrice"], request_dict["adultPrice"], request_dict["elderlyPrice"])
    
    for seat in request_dict["unavailableSeats"]:
        backend_connection.mark_seat_unavailable(seat, performance_id)

    return jsonify({
        "code": 200
    })

@api.route("/delete-performance", methods = ["POST"])
def delete_performance():
    logging.debug("API Delete Performance Triggered")
    request_dict = request.get_json()
    
    try:
        if backend_connection._check_performance_exists(request_dict["performanceID"]) == False:
            return jsonify({
                    "code": 401,
                    "message": "That performance does not exist."
                })
        
        backend_connection.delete_performance(request_dict["performanceID"])

        return jsonify({
            "code": 200
        })
    except:
        return jsonify({
            "code": 500,
            "message": "Something went wrong."
        })
    
@api.route("/add-showing", methods=["POST"])
def add_showing():
    logging.debug("Add Showing Triggered")
    request_dict = request.get_json()
    logging.debug(request_dict)

    try:
        performanceID = request_dict["performanceID"]

        logging.debug("Checking performance exists.")
        if backend_connection._check_performance_exists(performanceID) == False:
            logging.debug("Performance does not exist.")
            return jsonify({
                "code": 401,
                "message": "That performance does not exist."
            })
        logging.debug("Performance does exists, continuing.")
        date = request_dict["date"]

        backend_connection.add_showing(performanceID, datetime.strptime(date, "%Y-%m-%d"))
    except Exception as e:
        logging.critical(f"Something went wrong: {e}")
        return jsonify({
            "code": 500,
            "message": "Something went wrong."
        })