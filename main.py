# George Cooke Transfer Project
from backend import Backend
import logging
import flask
from flask import Flask, request, redirect, url_for, send_from_directory, flash
from api import api
import datetime

logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")
app.secret_key = 'super secret'

global data
data = Backend(database="PERSONAL")

# --------------------------- Login Page ---------------------------

@app.route("/", methods = ["GET"])
@app.route("/login", methods = ["GET"])
def login_page():
    return flask.render_template("login.html")

@app.route("/create-account", methods = ["GET"])
def create_account_page():
    return flask.render_template("create-account.html")

@app.route("/account-created", methods = ["GET"])
def account_created_page():
    return flask.render_template("account-created.html")

# --------------------------- Visitor Sections ---------------------------

@app.route("/visitor-dashboard", methods = ["GET"])
def visitor_dashboard():
    userID = flask.request.args.get("uid", default="None", type=int)

    if userID == "None" or data._check_user_exists(userID) == False:
        return redirect("/")
    return flask.render_template("visitor-events.html",
                                 userID=userID,
                                 userName = data.get_user_name(userID),
                                 performances = data.get_all_performances()
                                )

@app.route("/visitor-bookings", methods=["GET"])
def visitor_bookings():
    userID = flask.request.args.get("uid", default="None", type=int)

    if userID == "None" or data._check_user_exists(userID) == False:
        return redirect("/")
    return flask.render_template("visitor-my-bookings.html",
                                 userID = userID,
                                 userName = data.get_user_name(userID),
                                 bookings = data.get_user_bookings(userID)
                                 )

@app.route("/performance-showings", methods = ["GET"])
def performance_showings():
    userID = flask.request.args.get("uid", default="None", type=int)
    performanceID = flask.request.args.get("pid", default="None", type=int)

    if userID == "None" or data._check_user_exists(userID) == False:
        return redirect("/")
    return flask.render_template("visitor-select-showing.html",
                                 userID=userID,
                                 performanceID = performanceID,
                                 showings = data.get_all_performance_showings(performanceID),
                                 userName = data.get_user_name(userID),
                                 performanceName = data.get_performance_name(performanceID)
                                )

@app.route("/book-showing", methods=["GET"])
def book_showing():
    userID = flask.request.args.get("uid", default="None", type=int)
    showingID = flask.request.args.get("sid", default="None", type=int)

    performanceID = data.get_performanceID_from_showing(showingID)

    logging.debug(f"{data.get_unavailable_seats(showingID) = }")

    if userID == "None" or data._check_user_exists(userID) == False:
        return redirect("/")
    return flask.render_template("visitor-book-showing.html",
                                 userID = userID,
                                 showingID = showingID,
                                 performanceName = data.get_performance_name(performanceID),
                                 showingDate = data.get_showing_date(showingID),
                                 userName = data.get_user_name(userID),
                                 unavailableSeats = data.get_unavailable_seats(showingID)
                                )

@app.route("/thank-you")
def thank_you_page():
    bookingID = flask.request.args.get("bid", default="None", type=int)
    userID = flask.request.args.get("uid", default="None", type=int)

    showingID = data.get_booking_showing(bookingID)
    performanceID = data.get_showing_performance(showingID)
    tickets = data.get_booking_ticket_type_distributions(bookingID)

    if userID == "None" or data._check_user_exists(userID) == False:
        return redirect("/")
    return flask.render_template("visitor-thank-you.html",
                                 userID = userID,
                                 userName = data.get_user_name(userID),
                                 bookingID = bookingID,
                                 no_tickets = tickets,
                                 performance_name = data.get_performance_name(performanceID),
                                 showing_date = data.get_showing_date(showingID),
                                 price = data.get_booking_price(data.get_booking_user(bookingID), showingID, tickets[0], tickets[1], tickets[2])
                                 )

# --------------------------- Admin Sections ---------------------------

@app.route("/admin-dashboard", methods = ["GET"])
def admin_dashboard():
    performances = data.get_all_performances(date_from=datetime.date(year=1, month=1, day=1))
    showings = []

    for performance in performances:
        showing = data.admin_get_showings(performance[0])
        showings.append(showing)

    logging.debug(f"{performances = }")
    logging.debug(f"{showings = }")

    return flask.render_template("admin-dashboard.html",
                                 performances=performances,
                                 showings=showings,
                                 length = len(performances)
                                )

@app.route("/admin-add-event", methods = ["GET"])
def admin_add_event():
    return flask.render_template("admin-add-event.html")

@app.route("/admin-users", methods = ["GET"])
def admin_users():
    return flask.render_template("admin-users.html",
                                 users = data.get_all_users()
                                 )

# --------------------------- Main Running ---------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)