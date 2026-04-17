import pyodbc
import logging
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as colours
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Spacer, Paragraph, Table, SimpleDocTemplate

class Backend:
    def __init__(self, database:str = "COLLEGE") -> None:
        self.database = database

    def _connection(self) -> pyodbc.Connection:
        """
        An internal function used for the context manager to connect to the database.
        """

        if self.database == "PERSONAL":
            logging.debug("Connecting to personal (local) database...")

            cs = (
                    "Driver={ODBC Driver 18 for SQL Server};"
                    "Server=(localdb)\\TheatreBooking;"
                    "Database=TheatreBooking;"
                    "Trusted_Connection=yes;"
                )
        elif self.database == "COLLEGE":
            logging.debug("Connecting to college database...")
            logging.critical("College database has not yet been implemented!")
            raise Exception("College database has not yet been implemented.")
        else:
            logging.critical("Invalid database given.")
            raise Exception("Invalid database given.")
         
        logging.debug("Connected to database")

        connection = pyodbc.connect(cs)

        if connection is not None:
            return connection
        else:
            logging.critical("Could not connect to database")
            raise Exception("Could not connect to database")

    def _get_next_ID(self, table: str) -> int:
        """
        An internal function to get the next available primary key in one of the SQL tables
        """
        tables = ["Users", "Bookings", "BookingSeats", "Performances", "PerformanceUnavailableSeats", "Showings"]

        if table not in tables:
            raise Exception("Invalid table entered")

        strings = ["SELECT userID FROM dbo.Users ORDER BY userID DESC",
                   "SELECT bookingID FROM dbo.Bookings ORDER BY bookingID DESC",
                   "SELECT bookingSeatID FROM dbo.BookingSeats ORDER BY bookingSeatID DESC",
                   "SELECT performanceID FROM dbo.Performances ORDER BY performanceID DESC",
                   "SELECT performanceUnavailableSeatID FROM dbo.PerformanceUnavailableSeats ORDER BY performanceUnavailableSeatID DESC",
                   "SELECT ShowingID FROM dbo.Showings ORDER BY ShowingID DESC"]

        id_index = tables.index(table)
        select_string = strings[id_index]

        table = f"dbo.{table}"

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(select_string)

            past_ID = cursor.fetchone()
            logging.debug(f"{past_ID = }")

            if past_ID != None:
                new_ID = int(past_ID[0]) + 1
            else:
                new_ID = 1

            logging.debug(f"{new_ID = }")

        return new_ID

    def get_user_name(self, userID) -> str:
        """
        Used to get the name of the user to be displayed in the top right corner of the user pages for logout.
        """
        if self._check_user_exists(userID) == False:
            return ""
        
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT fName, lName FROM dbo.Users WHERE userID = ?", (userID))
            sql_response = cursor.fetchone()

            return f"{sql_response[0]} {sql_response[1]}"

    def check_password(self, email: str, password_attempt: str) -> tuple[bool, int, str]:
        """
        Checks if the entered password is correct for the email. Then returns a tuple with if the password is correct and (if correct) the relevant userID and user type.
        Universal admin login is email: "ADMIN", password: "AdminPassword123"
        """
        if email == "ADMIN" and password_attempt == "AdminPassword123":
            return (True, 0, "ADMIN")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT password, userID, userType FROM dbo.Users WHERE email = ?", (email))
            sql_response = cursor.fetchone()

            if sql_response == None: # Email not in database
                return (False, 0, "")
            
            correct_password = sql_response[0]
            userID = sql_response[1]
            user_type = sql_response[2]

            if correct_password == password_attempt:
                return (True, userID, user_type)
            else: # Incorrect password
                return (False, 0, "")

    def check_email_in_database(self, email: str) -> bool:
        """
        Checks if the provided email is already in use.
        Returns true if is in database (cannot be accepted)
        """
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM dbo.Users WHERE email = ?", (email))
            users = cursor.fetchall()

            logging.debug(f"{users = }")
            logging.debug(f"{len(users) = }")

            if len(users) == 0:
                return False
            else:
                return True

    def create_user(self, first_name: str, last_name: str, email: str, phone: str, password: str) -> None:
        """
        Creates a new user
        """
        if self.check_email_in_database(email):
            logging.critical("Email is already in email, not inserting!")
            raise Exception("Email is already in database, not inserting.")

        next_id = self._get_next_ID(table="Users")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("INSERT INTO dbo.Users VALUES(?, ?, ?, ?, ?, ?, ?)", (next_id, first_name, last_name, email, password, phone, "VISITOR"))
            
    def get_performanceID_from_showing(self, showingID) -> int: # TODO: Test get_performanceID_from_showing
        """
        Gets and returns the performanceID of the showing with the provided showingID.
        """

        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing does not exist.")
            raise Exception("Showing does not exist.")
        
        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting performances...")
            cursor.execute("SELECT performanceID FROM dbo.Showings WHERE showingID = ?", (showingID))
            performance_sql = cursor.fetchone()

            return performance_sql[0]
            
    def get_performance_name(self, performanceID) -> str:
        """
        Gets and returns the string name of the performance with the given ID.
        """

        if self._check_performance_exists(performanceID) == False:
            logging.critical("Performance does not exist")
            raise Exception("Performance does not exist")
        
        performanceID = int(performanceID)
        
        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting performances...")
            cursor.execute("SELECT title FROM dbo.Performances WHERE performanceID = ?", (performanceID))
            performance_sql = cursor.fetchone()

            return performance_sql[0]

    def get_all_performances(self, date_from: datetime.date = datetime.date.today()) -> list[tuple[int, str]]:
        """
        Gets and returns a list of all performances from and including the date provided sorted by ascending date.
        Returns in the format [(performanceID, performance title, description)]
        """
        if type(date_from) != datetime.date:
            logging.critical("Date_from given is not datetime.date")
            raise Exception("Date_from given is not datetime.date")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting performances...")
            cursor.execute("SELECT performanceID, title, performanceDescription FROM dbo.Performances WHERE performanceID IN (SELECT performanceID FROM dbo.Showings WHERE showingDate >= ?) OR performanceID IN (SELECT performanceID FROM dbo.Performances WHERE PerformanceID NOT IN (SELECT performanceID FROM dbo.Showings))", (date_from))
            performance_sql = cursor.fetchall()

            performances = [(performance[0], performance[1], performance[2]) for performance in performance_sql]

            logging.debug(f"{performances = }")
            
        return performances

    def get_all_performance_showings(self, performanceID: int) -> list[tuple[str, str]]:
        """
        Gets and returns a list of all showings for a performance.
        Returns in the format [(showingID: int, showing date: str)]
        """
        # Do I want this to be from a certain date?
        # Should it only show showings with available seats?
        if self._check_performance_exists(performanceID) == False:
            logging.critical("Performance does not exist, cannot get showings")
            raise Exception("Performance does not exist, cannot get showings")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting showings...")
            cursor.execute("SELECT showingID, showingDate FROM dbo.Showings WHERE performanceID = ? AND showingDate >= CAST(CURRENT_TIMESTAMP AS DATE)", (performanceID))
            results = cursor.fetchall()

            showings = []

            for showing in results:
                showingID = showing[0]
                showing_date = showing[1].strftime("%A %d %B, %Y")
                showings.append((showingID, showing_date))
            
        return showings

    def _check_valid_seat_ID(self, seatID: str) -> bool:
        """
        Validates if the specified seatID is valid.
        Returns true if valid, false if not.
        Used in the mark_seat_unavailable and book_seat functions
        """
        logging.debug(f"Checking seatID {seatID} is valid...")

        seat_letter = seatID[-1]
        seat_number = seatID[0:-1]

        if seat_letter not in list("ABCDEFGHIJKLMNOPQRST"):
            return False
        
        if seat_number.isnumeric() == False:
            return False
        
        if int(seat_number) > 10:
            return False
        
        return True

    def mark_seat_unavailable(self, seatID: str, performanceID: str) -> None:
        """
        Marks the specified seat as unavailable for the specified performance
        """
        if self._check_valid_seat_ID(seatID) == False:
            logging.critical("Invalid seatID given.")
            raise Exception("Invalid seatID given.")
        
        if self._check_performance_exists(performanceID) == False:
            logging.critical("Performance does not exist.")
            raise Exception("Performance does not exist.")

        next_id = self._get_next_ID("PerformanceUnavailableSeats")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Marking seat as unavailable...")
            cursor.execute("INSERT INTO dbo.PerformanceUnavailableSeats VALUES(?, ?, ?)", (next_id, performanceID, seatID))

    def delete_showing(self, showingID: int) -> None:
        """
        Deletes the showing and all associated records for the provided showingID.
        """

        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing does not exist.")
            raise Exception("Showing does not exist.")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("DELETE FROM dbo.Showings WHERE showingID = ?", (showingID))
            cursor.execute("DELETE FROM dbo.BookingSeats WHERE bookingID IN (SELECT bookingID FROM dbo.bookings WHERE showingID = ?)", (showingID))
            cursor.execute("DELETE FROM dbo.Bookings WHERE showingID =?", (showingID))

    def _check_showing_exists(self, showingID: int) -> bool:
        """
        Validates if a showing exists before booking to it or getting it's unavailable seats.
        Returns true if exists and can be used, returns false if it doesn't exist
        """
        if str(showingID).isnumeric() == False:
            logging.critical("ShowingID is not a number.")
            raise Exception("ShowingID is not numeric.")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM dbo.Showings WHERE showingID = ?", (showingID))
            showing = cursor.fetchone()

            if showing == None:
                return False
            else:
                return True

    def get_unavailable_seats(self, showingID: int) -> list[str]:
        """
        Gets and returns a list of all the unavailable seats for the specified showing.
        Includes booked seats and unavailable seats. Ordered alphabetically first by letter then number.
        """
        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing does not exist")
            raise Exception("Showing does not exist.")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT performanceID FROM dbo.Showings WHERE showingID = ?", (showingID))
            performanceID = cursor.fetchone()[0]

            cursor.execute("SELECT seatID FROM dbo.PerformanceUnavailableSeats WHERE performanceID = ?", (performanceID))
            unavailable_seats = cursor.fetchall()
            unavailable_seats = [[seat[0], "UNAVAILABLE"] for seat in unavailable_seats]

            cursor.execute("SELECT bookingID FROM dbo.Bookings WHERE showingID = ?", (showingID))
            bookingIDs = cursor.fetchall()
            if len(bookingIDs) == 1:
                bookingIDs = bookingIDs[0][0]
            else:
                bookingIDs = f"({",".join(str(bookingID[0]) for bookingID in bookingIDs)})"

            logging.debug(f"{bookingIDs = }")

            if type(bookingIDs) == int:
                cursor.execute("SELECT seatID FROM dbo.BookingSeats WHERE bookingID = ?", (bookingIDs))
                booked_seats = cursor.fetchall()
                booked_seats = [[seat[0], "BOOKED"] for seat in booked_seats]
            elif bookingIDs != "()":
                cursor.execute(f"SELECT seatID FROM dbo.BookingSeats WHERE bookingID IN {bookingIDs}")
                booked_seats = cursor.fetchall()
                booked_seats = [[seat[0], "BOOKED"] for seat in booked_seats]
            else:
                booked_seats = []

            unavailable_seats.extend(booked_seats)

            return unavailable_seats

    def _check_seat_available(self, seatID: str, showingID: int) -> bool:
        """
        Checks if a seat is available.
        Used in the book_seat function
        """
        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing does not exist")
            raise Exception("Showing does not exist")
        
        if self._check_valid_seat_ID(seatID) == False:
            logging.critical("Seat does not exist")
            raise Exception("Seat does not exist")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting seat from unavailable seats...")
            cursor.execute("SELECT performanceID FROM dbo.Showings WHERE showingID = ?", (showingID))
            performanceID = cursor.fetchone()[0]

            cursor.execute("SELECT seatID FROM dbo.PerformanceUnavailableSeats WHERE seatID = ? AND performanceID = ?", (seatID, performanceID))
            seat = cursor.fetchone()

            if seat != None:
                return False
            
            logging.debug("Getting seat from bookings...")
            cursor.execute("SELECT bookingID FROM dbo.Bookings WHERE showingID = ?", (showingID))
            bookings = cursor.fetchall()
            if len(bookings) == 1:
                bookings = bookings[0][0]
            else:
                bookings = f"({",".join(str(booking[0]) for booking in bookings)})"

            logging.debug(f"{bookings = }")

            if type(bookings) == int:
                cursor.execute("SELECT seatID FROM dbo.BookingSeats WHERE seatID = ? AND bookingID = ?", (seatID, bookings))
                booking = cursor.fetchone()

                if booking != None:
                    return False
            elif bookings != "()":
                cursor.execute(f"SELECT seatID FROM dbo.BookingSeats WHERE seatID = ? AND bookingID IN {bookings}", (seatID))
                booking = cursor.fetchone()

                if booking != None:
                    return False
            
        return True

    def book_seats(self, userID: int, seatIDs: list[str], showingID: int, seat_types: list[str]) -> int:
        """
        Books the specified seat for the specified showing and returns the bookingID
        """
        for seatID in seatIDs:
            if self._check_seat_available(seatID, showingID) == False:
                logging.critical(f"Seat {seatID} is not available, cannot book.")
                raise Exception(f"Seat {seatID} is not available, cannot book")
            
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist")
            raise Exception("User does not exist")
            
        if seatIDs == [] or seatIDs == None:
            logging.critical("No seatIDs given.")
            raise Exception("No seatIDs given")

        if len(seatIDs) != len(set(seatIDs)):
            logging.critical("Repeat seats present, cannot push")
            raise Exception("Repeat seats present, cannot push")
        
        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing does not exist")
            raise Exception("Showing does not exist")

        for seat_type in seat_types:
            if seat_type not in ["CHILD", "ADULT", "ELDERLY"]:
                logging.critical(f"Invalid seat type given: {seat_type}")
                raise Exception(f"Invalid seat type given: {seat_type}")
            
        if len(seatIDs) != len(seat_types):
            logging.critical("SeatIDs and seat_types length mismatch")
            raise Exception("SeatIDs and seat_types length mismatch")
        
        next_booking_id = self._get_next_ID("Bookings")
        
        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Adding booking...")
            cursor.execute("INSERT INTO dbo.Bookings VALUES(?, ?, ?)", (next_booking_id, showingID, userID))

            for i in range(len(seatIDs)):
                seatID = seatIDs[i]
                seat_type = seat_types[i]

                logging.debug(f"Booking seat {seatID} of type {seat_type} for showing {showingID}")

                next_booking_seat_id = self._get_next_ID("BookingSeats")

                cursor.execute("INSERT INTO dbo.BookingSeats VALUES(?, ?, ?, ?)", (next_booking_seat_id, next_booking_id, seatID, seat_type))
                cursor.commit()

        return next_booking_id

    def get_booking_price(self, userID: int, showingID: int, no_child_seats: int, no_adult_seats: int, no_elderly_seats: int) -> str:
        """
        Calculates the price for a potential booking based on specified values, userID is used to check if user is special guest.
        Returns in the format "£x.xx"
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist, cannot check user admin status.")
            raise Exception("User does not exist, cannot check user admin status.")
        
        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing doesn't exist.")
            raise Exception("Showing doesn't exist.")
        
        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting user type...")
            cursor.execute("SELECT userType FROM dbo.Users WHERE userID = ?", (userID))
            user_type = cursor.fetchone()[0]

            if user_type == "SPECIAL":
                return "£0.00"
            
            logging.debug("Getting prices...")
            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = (SELECT performanceID FROM dbo.Showings WHERE showingID = ?)", (showingID))
            prices = cursor.fetchone()

            price = (prices[0] * no_child_seats) + (prices[1] * no_adult_seats) + (prices[2] * no_elderly_seats)

            return f"£{price:.2f}"

    def get_user_bookings(self, userID: int, date_from: datetime.date = datetime.date.today()) -> list[tuple[int, str]]:
        """
        Gets and returns a list of all bookings for a user after the specified date (defaults to today).
        Returns in format [(bookingID: int, performance title: str, booking date: str)]
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist")
            raise Exception("User does not exist")
        
        if type(date_from) != datetime.date:
            logging.critical("Date from given is not datetime.date")
            raise Exception("Date from given is not datetime.date")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting bookings...")
            cursor.execute("SELECT bookingID, showingID FROM dbo.Bookings WHERE userID = ? AND showingID IN (SELECT showingID FROM dbo.Showings WHERE showingDate >= ?)", (userID, date_from))
            bookings_sql = cursor.fetchall()

            logging.debug(f"{bookings_sql = }")

            bookings = []

            for booking in bookings_sql:
                bookingID = booking[0]

                cursor.execute("SELECT title FROM dbo.Performances WHERE performanceID IN (SELECT performanceID FROM dbo.Showings WHERE showingID = ?)", (booking[1]))
                performance_title = cursor.fetchone()[0]

                cursor.execute("SELECT showingDate FROM dbo.Showings WHERE showingID = (SELECT showingID FROM dbo.Bookings WHERE bookingID = ?)", (bookingID))
                showing_date = cursor.fetchone()[0]

                showing_date = showing_date.strftime("%A %d %B, %Y")

                bookings.append((bookingID, performance_title, showing_date))
            
        return bookings

    def _check_booking_exists(self, bookingID: int):
        """
        Validates that a booking exists before generating its PDF ticket.
        Returns true if does exist and can be used, false if not
        """
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM dbo.Bookings WHERE bookingID = ?", (bookingID))
            booking = cursor.fetchone()

            if booking == None:
                return False
            else:
                return True

    def generate_pdf(self, bookingID: int) -> None:
        """
        Generates and saves a PDF ticket for the specified booking
        """
        if self._check_booking_exists(bookingID) == False:
            logging.critical("Booking does not exist, cannot generate ticket.")
            raise Exception("Booking does not exist, cannot generate ticket.")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting ticket information...")
            cursor.execute("SELECT showingID FROM dbo.Bookings WHERE bookingID = ?", (bookingID))
            showingID = cursor.fetchone()[0]

            logging.debug(f"{showingID = }")

            cursor.execute("SELECT showingDate FROM dbo.Showings WHERE showingID = ?", (showingID))
            date = cursor.fetchone()[0]
            date = date.strftime("%A %d %B, %Y")

            logging.debug(f"{date = }")

            cursor.execute("SELECT title, performanceID FROM dbo.Performances WHERE performanceID = (SELECT performanceID FROM dbo.Showings WHERE showingID = ?)", (showingID))
            sql_response  = cursor.fetchone()

            logging.debug(f"{sql_response = }")

            performance_title = sql_response[0]
            performanceID = sql_response[1]

            cursor.execute("SELECT fName, lName FROM dbo.Users WHERE userID = (SELECT userID FROM dbo.Bookings WHERE bookingID = ?)", (bookingID))
            sql_response = cursor.fetchone()
            name = f"{sql_response[0]} {sql_response[1]}"

            cursor.execute("SELECT seatID, bookingType FROM dbo.BookingSeats WHERE bookingID = ?", (bookingID))
            seats = cursor.fetchall()
            
            adult_seats = 0
            child_seats = 0
            elderly_seats = 0
            
            for seat in seats:
                if seat[1] == "ADULT":
                    adult_seats += 1
                elif seat[1] == "CHILD":
                    child_seats += 1
                elif seat[1] == "ELDERLY":
                    elderly_seats += 1
                else:
                    logging.critical("Invalid seat type.")
                    raise Exception("Invalid seat type.")
                
            cursor.execute("SELECT userID FROM dbo.Bookings WHERE bookingID = ?", (bookingID))
            userID = cursor.fetchone()[0]
            
        price = self.get_booking_price(userID, performanceID, child_seats, adult_seats, elderly_seats)
        
        doc = SimpleDocTemplate("Ticket.pdf", pagesize = A4)
        doc_build_string = []

        title = Paragraph(f"Collyer's Event Ticket", style=ParagraphStyle(
            "LeftAligned",
            alignment=TA_LEFT,
            fontName="Helvetica-Bold",
            fontSize=35
        ))
        doc_build_string.extend([title, Spacer(1, 30)])

        performance_name = Paragraph(f"{performance_title}", style=ParagraphStyle(
            "LeftAligned",
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=35
        ))
        doc_build_string.extend([performance_name, Spacer(1, 30)])

        date_paragraph = Paragraph(f"{date}", style=ParagraphStyle(
            "LeftAligned",
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=20
        ))
        doc_build_string.extend([date_paragraph, Spacer(1, 30)])
        
        name_paragraph = Paragraph(f"{name}", style=ParagraphStyle(
            "LeftAligned",
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=35
        ))
        doc_build_string.extend([name_paragraph, Spacer(1, 50)])

        for seat in seats:
            seat_paragraph = Paragraph(f"{seat[0]} - {seat[1]}", style=ParagraphStyle(
                "LeftAligned",
                alignment=TA_LEFT,
                fontName="Helvetica",
                fontSize=15
            ))
            doc_build_string.extend([seat_paragraph, Spacer(1, 10)])

        children_paragraph = Paragraph(f"Child Seats: {child_seats}", style=ParagraphStyle(
            "LeftAligned",
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=20
        ))
        doc_build_string.extend([Spacer(1, 20), children_paragraph, Spacer(1, 15)])

        adult_paragraph = Paragraph(f"Adult Seats: {adult_seats}", style=ParagraphStyle(
            "LeftAligned",
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=20
        ))
        doc_build_string.extend([adult_paragraph, Spacer(1, 15)])

        elderly_paragraph = Paragraph(f"Elderly Seats: {elderly_seats}", style=ParagraphStyle(
            "LeftAligned",
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=20
        ))
        doc_build_string.extend([elderly_paragraph, Spacer(1, 15)])

        total_paid_paragraph = Paragraph(f"Total Paid: {price}", style=ParagraphStyle(
            "LeftAligned",
            alignment=TA_LEFT,
            fontName="Helvetica-Bold",
            fontSize=20
        ))
        doc_build_string.extend([total_paid_paragraph, Spacer(1, 30)])

        doc.build(doc_build_string)

    def _validate_new_performance_prices(self, child_price: float, adult_price: float, elderly_price: float) -> bool:
        """
        Validates the number of decimal places and digits of the proposed prices. Returns False if invalid or True if valid.
        Constraints are that there must not be more than 5 digits before the decimal place and that there may not be more than 2 digits after the decimal place.
        """

        if child_price >= 100_000 or adult_price >= 100_000 or elderly_price >= 100_000:
            logging.critical("Price with more than 5 digits before decimal entered, not entering.")
            return False
        
        child_split = str(child_price).split(".")
        adult_split = str(adult_price).split(".")
        elderly_split = str(elderly_price).split(".")

        if len(child_split) == 2:
            if len(child_split[1]) > 2:
                logging.critical(f"Child price has too many decimal places given. {child_price = }")
                return False
            
        if len(adult_split) == 2:
            if len(adult_split[1]) > 2:
                logging.critical(f"Adult price has too many decimal places given. {adult_price = }")
                return False
            
        if len(elderly_split) == 2:
            if len(elderly_split[1]) > 2:
                logging.critical(f"Elderly price has too many decimal places given. {elderly_price = }")
                return False
            
        return True

    def add_performance(self, title: str, description: str, child_price: float = 5, adult_price: float = 10, elderly_price: float = 5) -> int:
        """
        Adds the event and returns the performanceID for the new performance so that showings can be added
        """
        if self._validate_new_performance_prices(child_price=child_price, adult_price=adult_price, elderly_price=elderly_price) == False:
            raise Exception("Failed price validation")

        next_id = self._get_next_ID(table="Performances")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Adding new performance...")
            cursor.execute("INSERT INTO dbo.Performances VALUES(?, ?, ?, ?, ?, ?)", (next_id, title, description, child_price, adult_price, elderly_price))
            
        return next_id
    
    def _check_performance_exists(self, performanceID) -> bool:
        """
        Validation for checking a performance exists before pushing to it.
        Returns true if the performance exists, false if it doesn't
        """
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM dbo.Performances WHERE performanceID = ?", (performanceID))
            performance = cursor.fetchone()

            if performance == None:
                return False
            else:
                return True

    def add_showing(self, performanceID: int, date: datetime.date = datetime.date.today()) -> int:
        """
        Adds a new showing to for the performance with the given performanceID on the specified date. Returns the newly added showingID
        """
        logging.debug("Made it to add_showing backend")
        if self._check_performance_exists(performanceID) == False:
            logging.critical("PerformanceID does not exist.")
            raise Exception("PerformanceID does not exist.")

        """DOES NOT WORK - if type(date) != datetime.date or type(date) != datetime.datetime:
            logging.critical(f"Date format is invalid. Expected datetime.date or datetime.datetime, got {type(date)}.")
            raise Exception(f"Date format is invalid. Expected datetime.date or datetime.datetime, got {type(date)}.")"""

        next_id = self._get_next_ID(table="Showings")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Creating new showing...")
            cursor.execute("INSERT INTO dbo.Showings VALUES(?, ?, ?)", (next_id, performanceID, date))
            
        return next_id
    
    def get_showing_date(self, showingID: int) -> str:
        """
        Gets and returns as string date for the provided showingID.
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT showingDate FROM dbo.Showings WHERE showingID = ?", (showingID))
            showing_date = cursor.fetchone()[0]

            return showing_date.strftime("%A %d %B, %Y")

    def admin_get_showings(self, performanceID: int) -> list[tuple[int, str, int, list[str]]]:
        """
        Gets and returns all showings for an event and returns in the following format: [(showingID: int, showing date: str, empty seats: int, revenue, showing attendees (names): list)]
        The showing attendees will be made up of the following tuples [(userID, user first name, user last name, user phone)] and will be sorted by ascending surname alphabetically
        """
        if self._check_performance_exists(performanceID) == False:
            logging.critical("PerformanceID does not exist.")
            raise Exception("PerformanceID does not exist.")

        with self._connection() as connection: # TODO: Check if more efficient way of doing this - May be able to combine into one SQL statement
            cursor = connection.cursor()

            logging.debug(f"Getting showings for {performanceID}...")
            cursor.execute("SELECT showingID, showingDate FROM dbo.Showings WHERE performanceID = ? ORDER BY showingDate ASC", (performanceID))
            showings_result = cursor.fetchall()

            showings = []

            for showing in showings_result:
                showingID = showing[0]
                showing_date = showing[1]
                showing_date = showing_date.strftime("%A %d %B, %Y") # this likely won't work on the college servers because of different SQL versions
                remaining_seats = 200

                cursor.execute("SELECT userID FROM dbo.Bookings WHERE showingID = ?", (showingID))
                users_result = cursor.fetchall()

                attendees = []

                for user in users_result:
                    userID = user[0]
                    
                    cursor.execute("SELECT fName, lName, phone FROM dbo.Users WHERE userID = ? ORDER BY lName ASC", (userID))
                    user_details = cursor.fetchone()

                    logging.debug(f"{user_details = }")

                    user_first_name = user_details[0]
                    user_last_name = user_details[1]
                    user_phone = user_details[2]

                    attendees.append((userID, user_first_name, user_last_name, user_phone))

                attendees.sort(key=lambda x:x[2])

                remaining_seats -= len(self.get_unavailable_seats(showingID))

                showings.append((showingID, showing_date, remaining_seats, self.calculate_showing_revenue(showingID), attendees))

            logging.debug(f"{showings = }")

            return showings

    def get_all_users(self) -> list[tuple[int, str, str, str, str]]:
        """
        Gets and returns a list of all users (sorted alphabetically by surname) in the following format [(userID: int, first name: str, last name: str, phone: str, userType: str)]
        """
        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting users...")
            cursor.execute("SELECT userID, fName, lName, phone, userType FROM dbo.Users")
            users = cursor.fetchall()

            users = [tuple(row) for row in users]
            
        return users
    
    def _check_user_exists(self, userID: int) -> bool:
        """
        Used in the validation of change_user_type, get_booking_price and delete_user to check that the user exists.
        Returns true if the user exists, false if they do not.
        """
        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Checking user exists...")
            cursor.execute("SELECT * FROM dbo.Users WHERE userID = ?", (userID))
            user = cursor.fetchone()

            if user == None:
                return False
            else:
                return True

    def change_user_type(self, userID: int, new_type: str) -> None:
        """
        Changes the user type of the specified user to the one provided
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist, cannot update type.")
            raise Exception("User does not exist, cannot update type.")
        
        if new_type not in ["VISITOR", "SPECIAL", "ADMIN"]:
            logging.critical("New user type is invalid.")
            raise Exception("New user type is invalid")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug(f"Changing user {userID} to {new_type}...")
            cursor.execute("UPDATE dbo.Users SET userType = ? WHERE userID = ?", (new_type, userID))

    def delete_user(self, userID: int) -> None:
        """
        Deletes the provided user
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist, cannot delete user.")
            raise Exception("User does not exist, cannot delete user.")

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug(f"Deleting user {userID}...")
            cursor.execute("DELETE FROM dbo.Users WHERE userID =?", (userID))

    def delete_performance(self,performanceID) -> None:
        """
        Deletes the provided performance and any showings associated with it.
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug(f"Deleting performance {performanceID}...")
            cursor.execute("DELETE FROM dbo.PerformanceUnavailableSeats WHERE performanceID = ?", (performanceID))
            cursor.execute("DELETE FROM dbo.BookingSeats WHERE bookingID IN (SELECT bookingID FROM dbo.Bookings WHERE showingID IN (SELECT showingID FROM dbo.Showings WHERE performanceID = ?))", (performanceID))
            cursor.execute("DELETE FROM dbo.Bookings WHERE showingID IN (SELECT showingID FROM dbo.Showings WHERE performanceID = ?)", (performanceID))
            cursor.execute("DELETE FROM dbo.Showings WHERE performanceID =?", (performanceID))
            cursor.execute("DELETE FROM dbo.Performances WHERE performanceID = ?", (performanceID))

    def check_user_admin(self, userID: int) -> bool:
        """
        Checks if the user is an admin and returns true if they are. To be used for sending to the relevant portal
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist, cannot check user admin status.")
            raise Exception("User does not exist, cannot check user admin status.")
        
        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug(f"Checking user {userID} for admin privileges...")
            cursor.execute("SELECT userType FROM dbo.Users WHERE userID = ?", (userID))
            user_type = cursor.fetchone()[0]

            if user_type == "ADMIN":
                return True
            else:
                return False
            
    def get_booking_showing(self, bookingID: int) -> int:
        """
        Gets and returns the showingID of the given bookingID
        """

        if self._check_booking_exists(bookingID) == False:
            logging.critical("Booking does not exist, cannot check showingID")
            raise Exception("Booking does not exist, cannot check showingID")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT showingID FROM dbo.Bookings WHERE bookingID = ?", (bookingID))
            return int(cursor.fetchone()[0])

    def get_showing_performance(self, showingID: int) -> int:
        """
        Gets and returns the performanceID of the given showingID.
        """

        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing does not exist, cannot check performanceID")
            raise Exception("Showing does not exist, cannot check performanceID")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT performanceID FROM dbo.Showings WHERE showingID = ?", (showingID))
            return int(cursor.fetchone()[0])
        
    def get_booking_ticket_type_distributions(self, bookingID: int) -> tuple[int, int, int]:
        """
        Gets and returns the distribution of a booking's tickets types and returns in the the format (child tickets, adult tickets, elderly tickets)
        """

        if self._check_booking_exists(bookingID) == False:
            logging.critical("Booking does not exist, cannot check distributions")
            raise Exception("Booking does not exist, cannot check distributions")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT bookingType from dbo.BookingSeats WHERE bookingID = ?", (bookingID))
            seats = cursor.fetchall()

        child, adult, elderly = 0, 0, 0

        for seat in seats:
            seat = seat[0]
            if seat == "CHILD": child += 1
            elif seat =="ADULT": adult += 1
            elif seat == "ELDERLY": elderly += 1
            else:
                logging.critical("Unknown seat type when getting distributions.")
                raise ValueError("Unknown seat type when getting distributions.")
            
        return (child, adult, elderly)
    
    def get_booking_user(self, bookingID: int) -> int:
        """
        Gets and returns the userID for the provided bookingID.
        """

        if self._check_booking_exists(bookingID) == False:
            logging.critical("Booking does not exist, cannot check userID")
            raise Exception("Booking does not exist, cannot check userID")
        
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT userID FROM dbo.Bookings WHERE bookingID = ?", (bookingID))
            return cursor.fetchone()
        
    def calculate_showing_revenue(self, showingID: int) -> str:
        """
        Gets and returns the total revenue for the given showing.
        """

        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing does not exist, cannot get revenue")
            raise Exception("Showing does not exist, cannot get revenue")
        
        with self._connection() as connection:
            cursor = connection.cursor()
            
            cursor.execute("SELECT bookingID, userID FROM dbo.Bookings WHERE showingID = ?", (showingID))
            bookingIDs = cursor.fetchall()

            bookingIDs_array = []

            for bookingID in bookingIDs:
                cursor.execute("SELECT userType FROM dbo.Users WHERE userID = ?", (bookingID[1]))
                if cursor.fetchone()[0] != "SPECIAL":
                    bookingIDs_array.append(str(bookingID[0]))

            if len(bookingIDs_array) == 0:
                return "£0.00"

            in_string = f"({",".join(bookingIDs_array)})"
            logging.debug(f"{in_string = }")

            cursor.execute(f"SELECT bookingType FROM dbo.BookingSeats WHERE bookingID IN {in_string}")
            seat_types = cursor.fetchall()

            child, adult, elderly = 0, 0, 0

            for seat in seat_types:
                seat = seat[0]
                if seat == "CHILD": child += 1
                elif seat =="ADULT": adult += 1
                elif seat == "ELDERLY": elderly += 1
                else:
                    logging.critical("Unknown seat type when getting distributions.")
                    raise ValueError("Unknown seat type when getting distributions.")
                
            performanceID = self.get_performanceID_from_showing(showingID)
            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (performanceID))
            prices = cursor.fetchone()

            total = (child * prices[0]) + (adult * prices[1]) + (adult * prices[2])

        return f"£{total:.2f}"

    def search_user(self, text: str) -> list[tuple[int, str, str, str, str]]:
        """
        Gets and returns a list of all users that fit the search criteria (the provided string is alike to at least of of: fName, lName, or phone) and returns in format [(userID, fName, lName, phone, userType)]
        """

        new_text = f"%{text}%"

        with self._connection() as connection:
            cursor = connection.cursor()

            logging.debug("Getting users...")
            cursor.execute("SELECT userID, fName, lName, phone, userType FROM dbo.Users WHERE fName LIKE ? OR lName LIKE ? OR phone LIKE ?", (new_text, new_text, new_text)) # TODO: Make work with % - Changed to have % symbol but now doesn't work
            users = cursor.fetchall()

            users = [tuple(row) for row in users]
            
        return users

logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")