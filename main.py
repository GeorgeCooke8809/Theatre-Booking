from backend import Backend
import logging
import flask
from flask import Flask, request, redirect, url_for, send_from_directory
from api import api

logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")

global data
data = Backend(database="PERSONAL")

@app.route("/", methods = ["GET"])
@app.route("/login", methods = ["GET"])
def login_page():
    return flask.render_template("login.html")

@app.route("/visitor-dashboard", methods = ["GET"])
def visitor_dashboard(userID):
    return f"<h1>Visitor Dashboard - {userID = }</h1>"

@app.route("/admin-dashboard", methods = ["GET"])
def admin_dashboard():
    return f"<h1>Admin Dashboard</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)