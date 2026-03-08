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
        pass

    def get_all_performance_showings(self, performanceID: int) -> list[tuple[str, str]]:
        """
        Gets and returns a list of all showings for a performance.
        Returns in the format [[showingID: int, showing date: str]]
        """
        #TODO: Implement - get_all_performance_showings
        pass

    def get_unavailable_seats(self, showingID: int) -> list[str]:
        """
        Gets and returns a list of all the unavailable seats for the specified showing
        """
        #TODO: Implement - get_unavailable_seats
        pass

    def book_seat(self, seatID: str, showingID: int, seat_type: str) -> None:
        """
        Books the specified seat for the specified showing
        """
        #TODO: Implement - book_seat
        pass

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
                cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?" (performanceID))
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
        #TODO: Implement - get_user_bookings
        pass

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

    def admin_get_showings(self, performanceID: int) -> list[tuple[int, str, list[str]]]:
        """
        Gets and returns all showings for an event and returns in the following format: [(showingID: int, showing date: str, showing attendees (names): list)]
        """
        #TODO: Implement - admin_get_showings
        pass

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