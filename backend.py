import pyodbc
import logging
import datetime

class Backend:
    def __init__(self, database:str = "COLLEGE") -> None:
        self.database = database

    def _connection(self):
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

        return pyodbc.connect(cs)

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
            if connection is not None:
                cursor = connection.cursor()

                cursor.execute(select_string)

                past_ID = cursor.fetchone()
                logging.debug(f"{past_ID = }")

                if past_ID != None:
                    new_ID = int(past_ID[0]) + 1
                else:
                    new_ID = 1

                logging.debug(f"{new_ID = }")
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

        return new_ID

    def check_password(self, email: str, password_attempt: str) -> bool:
        """
        Checks if the entered password is correct for the email
        """
        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                cursor.execute("SELECT password FROM dbo.Users WHERE email = ?", (email))
                correct_password = cursor.fetchone()

                if correct_password == None: # Email not in database
                    return False

                if correct_password[0] == password_attempt:
                    return True
                else: # Incorrect password
                    return False
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def check_email_in_database(self, email: str) -> bool:
        """
        Checks if the provided email is already in use.
        Returns true if is in database (cannot be accepted)
        """
        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                cursor.execute("SELECT * FROM dbo.Users WHERE email = ?", (email))
                users = cursor.fetchall()

                logging.debug(f"{users = }")
                logging.debug(f"{len(users) = }")

                if len(users) == 0:
                    return False
                else:
                    return True
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def create_user(self, first_name: str, last_name: str, email: str, phone: str, password: str) -> None:
        """
        Creates a new user
        """
        if self.check_email_in_database(email):
            logging.critical("Email is already in email, not inserting!")
            raise Exception("Email is already in database, not inserting.")

        with self._connection() as connection:
            next_id = self._get_next_ID(table="Users")

            if connection is not None:
                cursor = connection.cursor()

                cursor.execute("INSERT INTO dbo.Users VALUES(?, ?, ?, ?, ?, ?, ?)", (next_id, first_name, last_name, email, password, phone, "VISITOR"))
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def get_all_performances(self, date_from: datetime.date = datetime.date.today()) -> list[tuple[int, str]]:
        """
        Gets and returns a list of all performances from and including the date provided sorted by ascending date.
        Returns in the format [(performanceID, performance title)]
        """
        #TODO: Implement - get_all_performances
        if type(date_from) != datetime.date:
            logging.critical("Date_from given is not datetime.date")
            raise Exception("Date_from given is not datetime.date")

        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                logging.debug("Getting performances...")
                cursor.execute("SELECT performanceID, title FROM dbo.Performances WHERE performanceID IN (SELECT performanceID FROM dbo.Showings WHERE showingDate >= ?)", (date_from))
                performance_sql = cursor.fetchall()

                performances = [(performance[0], performance[1]) for performance in performance_sql]

                logging.debug(f"{performances = }")
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")
            
        return performances

    def get_all_performance_showings(self, performanceID: int) -> list[tuple[str, str]]:
        """
        Gets and returns a list of all showings for a performance.
        Returns in the format [(showingID: int, showing date: str)]
        """
        #TODO: Implement - get_all_performance_showings
        with self._connection() as connection:
            next_id = self._get_next_ID("PerformanceUnavailableSeats")

            if connection is not None:
                cursor = connection.cursor()

                logging.debug("Marking seat as unavailable...")
                cursor.execute("INSERT INTO dbo.PerformanceUnavailableSeats VALUES(?, ?, ?)", (next_id, performanceID, seatID))
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

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

        with self._connection() as connection:
            next_id = self._get_next_ID("PerformanceUnavailableSeats")

            if connection is not None:
                cursor = connection.cursor()

                logging.debug("Marking seat as unavailable...")
                cursor.execute("INSERT INTO dbo.PerformanceUnavailableSeats VALUES(?, ?, ?)", (next_id, performanceID, seatID))
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def _check_showing_exists(self, showingID: int) -> bool:
        """
        Validates if a showing exists before booking to it or getting it's unavailable seats.
        Returns true if exists and can be used, returns false if it doesn't exist
        """
        if str(showingID).isnumeric() == False:
            logging.critical("ShowingID is not a number.")
            raise Exception("ShowingID is not numeric.")

        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                cursor.execute("SELECT * FROM dbo.Showings WHERE showingID = ?", (showingID))
                showing = cursor.fetchone()

                if showing == None:
                    return False
                else:
                    return True
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def get_unavailable_seats(self, showingID: int) -> list[str]:
        """
        Gets and returns a list of all the unavailable seats for the specified showing.
        Includes booked seats and unavailable seats. Ordered alphabetically first by letter then number.
        """
        if self._check_showing_exists(showingID) == False:
            logging.critical("Showing does not exist")
            raise Exception("Showing does not exist.")

        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                cursor.execute("SELECT performanceID FROM dbo.Showings WHERE showingID = ?", (showingID))
                performanceID = cursor.fetchone()[0]

                cursor.execute("SELECT seatID FROM dbo.PerformanceUnavailableSeats WHERE performanceID = ?", (performanceID))
                unavailable_seats = cursor.fetchall()
                unavailable_seats = [seat[0] for seat in unavailable_seats]

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
                    booked_seats = [seat[0] for seat in booked_seats]
                elif bookingIDs != "()":
                    cursor.execute(f"SELECT seatID FROM dbo.BookingSeats WHERE bookingID IN {bookingIDs}")
                    booked_seats = cursor.fetchall()
                    booked_seats = [seat[0] for seat in booked_seats]
                else:
                    booked_seats = []

                unavailable_seats.extend(booked_seats)
                unavailable_seats.sort(key = lambda x: f"{x[-1]}{int(x[0:-1]):02d}")

                return unavailable_seats
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")
            
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
            if connection is not None:
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
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")
            
        return True

    def book_seats(self, userID: int, seatIDs: list[str], showingID: int, seat_types: list[str]) -> None:
        """
        Books the specified seat for the specified showing
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
            if connection is not None:
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
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def get_booking_price(self, userID: int, performanceID: int, no_child_seats: int, no_adult_seats: int, no_elderly_seats: int) -> str:
        """
        Calculates the price for a potential booking based on specified values, userID is used to check if user is special guest.
        Returns in the format "£x.xx"
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist, cannot check user admin status.")
            raise Exception("User does not exist, cannot check user admin status.")
        
        if self._check_performance_exists(userID) == False:
            logging.critical("Performance doesn't exist.")
            raise Exception("Performance doesn't exist.")
        
        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                logging.debug("Getting user type...")
                cursor.execute("SELECT userType FROM dbo.Users WHERE userID = ?", (userID))
                user_type = cursor.fetchone()[0]

                if user_type == "SPECIAL":
                    return "£0.00"
                
                logging.debug("Getting prices...")
                cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (performanceID))
                prices = cursor.fetchone()

                price = (prices[0] * no_child_seats) + (prices[1] * no_adult_seats) + (prices[2] * no_elderly_seats)

                return f"£{price:.2f}"
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def get_user_bookings(self, userID: int, date_from: datetime.date = datetime.date.today()) -> list[tuple[int, str]]:
        """
        Gets and returns a list of all bookings for a user after the specified date (defaults to today).
        Returns in format [(bookingID: int, booking title: str)]
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist")
            raise Exception("User does not exist")
        
        if type(date_from) != datetime.date:
            logging.critical("Date from given is not datetime.date")
            raise Exception("Date from given is not datetime.date")

        with self._connection() as connection:
            if connection is not None:
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

                    bookings.append((bookingID, performance_title))
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")
            
        return bookings

    def generate_pdf(self, bookingID: int) -> None:
        """
        Generates and saves a PDF ticket for the specified booking
        """
        #TODO: Implement - generate_pdf
        pass

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

        with self._connection() as connection:
            next_id = self._get_next_ID(table="Performances")

            if connection is not None:
                cursor = connection.cursor()

                logging.debug("Adding new performance...")
                cursor.execute("INSERT INTO dbo.Performances VALUES(?, ?, ?, ?, ?, ?)", (next_id, title, description, child_price, adult_price, elderly_price))
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")
            
        return next_id
    
    def _check_performance_exists(self, performanceID) -> bool:
        """
        Validation for checking a performance exists before pushing to it.
        Returns true if the performance exists, false if it doesn't
        """
        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                cursor.execute("SELECT * FROM dbo.Performances WHERE performanceID = ?", (performanceID))
                performance = cursor.fetchone()

                if performance == None:
                    return False
                else:
                    return True
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def add_showing(self, performanceID: int, date: datetime.date = datetime.date.today()) -> int:
        """
        Adds a new showing to for the performance with the given performanceID on the specified date. Returns the newly added showingID
        """
        if self._check_performance_exists(performanceID) == False:
            logging.critical("PerformanceID does not exist.")
            raise Exception("PerformanceID does not exist.")

        if type(date) != datetime.date:
            logging.critical(f"Date format is invalid. Expected datetime.date, got {type(date)}.")
            raise Exception(f"Date format is invalid. Expected datetime.date, got {type(date)}.")

        with self._connection() as connection:
            next_id = self._get_next_ID(table="Showings")

            if connection is not None:
                cursor = connection.cursor()

                logging.debug("Creating new showing...")
                cursor.execute("INSERT INTO dbo.Showings VALUES(?, ?, ?)", (next_id, performanceID, date))
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")
            
        return next_id

    def admin_get_showings(self, performanceID: int) -> list[tuple[int, str, int, list[str]]]:
        """
        Gets and returns all showings for an event and returns in the following format: [(showingID: int, showing date: str, empty seats: int, showing attendees (names): list)]
        The showing attendees will be made up of the following tuples [(userID, user first name, user last name, user phone)] and will be sorted by ascending surname alphabetically
        """
        if self._check_performance_exists(performanceID) == False:
            logging.critical("PerformanceID does not exist.")
            raise Exception("PerformanceID does not exist.")

        with self._connection() as connection:
            if connection is not None:
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
                        
                        cursor.execute("SELECT fName, lName, phone FROM dbo.Users WHERE userID = ?", (userID))
                        user_details = cursor.fetchone()

                        logging.debug(f"{user_details = }")

                        user_first_name = user_details[0]
                        user_last_name = user_details[1]
                        user_phone = user_details[2]

                        attendees.append((userID, user_first_name, user_last_name, user_phone))

                    attendees.sort(key=lambda x:x[2])

                    remaining_seats -= len(self.get_unavailable_seats(showingID))

                    showings.append((showingID, showing_date, remaining_seats, attendees))

                logging.debug(f"{showings = }")

                return showings
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def get_all_users(self) -> list[tuple[int, str, str, str, str]]:
        """
        Gets and returns a list of all users (sorted alphabetically by surname) in the following format [(userID: int, first name: str, last name: str, phone: str, userType: str)]
        """
        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                logging.debug("Getting users...")
                cursor.execute("SELECT userID, fName, lName, phone, userType FROM dbo.Users")
                users = cursor.fetchall()

                users = [tuple(row) for row in users]
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")
            
        return users
    
    def _check_user_exists(self, userID: int) -> bool:
        """
        Used in the validation of change_user_type, get_booking_price and delete_user to check that the user exists.
        Returns true if the user exists, false if they do not.
        """
        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                logging.debug("Checking user exists...")
                cursor.execute("SELECT * FROM dbo.Users WHERE userID = ?", (userID))
                user = cursor.fetchone()

                if user == None:
                    return False
                else:
                    return True
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

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
            if connection is not None:
                cursor = connection.cursor()

                logging.debug(f"Changing user {userID} to {new_type}...")
                cursor.execute("UPDATE dbo.Users SET userType = ? WHERE userID = ?", (new_type, userID))
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def delete_user(self, userID: int) -> None:
        """
        Deletes the provided user
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist, cannot delete user.")
            raise Exception("User does not exist, cannot delete user.")

        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                logging.debug(f"Deleting user {userID}...")
                cursor.execute("DELETE FROM dbo.Users WHERE userID =?", (userID))
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

    def check_user_admin(self, userID: int) -> bool:
        """
        Checks if the user is an admin and returns true if they are. To be used for sending to the relevant portal
        """
        if self._check_user_exists(userID) == False:
            logging.critical("User does not exist, cannot check user admin status.")
            raise Exception("User does not exist, cannot check user admin status.")
        
        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                logging.debug(f"Checking user {userID} for admin privileges...")
                cursor.execute("SELECT userType FROM dbo.Users WHERE userID = ?", (userID))
                user_type = cursor.fetchone()[0]

                if user_type == "ADMIN":
                    return True
                else:
                    return False
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")