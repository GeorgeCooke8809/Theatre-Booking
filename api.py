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