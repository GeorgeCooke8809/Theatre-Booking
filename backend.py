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
        else:
            logging.debug("Connecting to college database...")
            logging.critical("College database has not yet been implemented!")
            raise Exception("College database has not yet been implemented.")
         
        logging.debug("Connected to database")

        return pyodbc.connect(cs)

    def _get_next_ID(self, table: str) -> int:
        """
        An internal function to get the next available primary key in one of the SQL tables
        """
        #TODO: Implement - _get_next_ID

        tables = ["Users", "Bookings", "BookingSeats", "Performances", "PerformanceUnavailableSeats", "Showings"]

        if table not in tables:
            raise Exception("Invalid table entered")

        ids = ["userID", "bookingID", "bookingSeatID", "performanceID", "performanceUnavailableSeatID", "showingID"]

        id_index = tables.index(tables)
        select = ids[id_index]

        table = f"dbo.{table}"

        with self._connection() as connection:
            if connection is not None:
                cursor = connection.cursor()

                cursor.execute("SELECT ? FROM ? ORDER BY userID DESC", (select, table))

                past_ID = cursor.fetchone()
                logging.debug(f"{past_ID = }")

                if past_ID != None:
                    new_ID = int(past_ID[0]) + 1
                else:
                    new_ID = 1
            else:
                logging.critical("Could not connect to database")
                raise Exception("Could not connect to database")

        return new_ID

    def check_password(self, email: str, password_attempt: str) -> bool:
        """
        Checks if the entered password is correct for the email
        """
        #TODO: Implement - check_password
        pass

    def check_email_in_database(self, email: str) -> bool:
        """
        Checks if the provided email is already in use.
        Returns true if is in database (cannot be accepted)
        """
        #TODO: Implement - check_email_in_database
        pass

    def create_user(self, first_name: str, last_name: str, email: str, phone: str, password: str) -> None:
        """
        Creates a new user
        """
        #TODO: Implement - create_user
        pass

    def get_all_performances(self, date_from: datetime.date = datetime.date.today()) -> list[str]:
        """
        Gets and returns a list of all performances from and including the date provided sorted by ascending date
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

    def get_booking_price(self, userID: int, performanceID: int, child_seats: int, adult_seats: int, elderly_seats: int) -> float:
        """
        Calculates the price for a potential booking based on specified values, userID is used to check if user is special guest
        """
        #TODO: Implement - get_booking_price
        pass

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

    def add_event(self, title: str, description: str, child_price: float = 5, adult_price: float = 10, elderly_price: float = 5) -> int:
        """
        Adds the event and returns the performanceID for the new performance so that showings can be added
        """
        #TODO: Implement - add_event
        pass

    def add_showing(self, performanceID: int, date: datetime.date = datetime.date.today()) -> None:
        """
        Adds a new showing to for the performance with the given performanceID on the specified date
        """
        #TODO: Implement - add_showing
        pass

    def admin_get_showings(self, performanceID: int) -> list[tuple[int, str, list[str]]]:
        """
        Gets and returns all showings for an event and returns in the following format: [(showingID: int, showing date: str, showing attendees (names): list)]
        """
        #TODO: Implement - admin_get_showings
        pass

    def get_all_users(self) -> list[tuple[int, str, str, str, str]]:
        """
        Gets and returns a list of all users (sorted alphabetically by surname) in the following format [(userID: int, first name: str, last name: str, phone: str, type: str)]
        """
        #TODO: Implement - get_all_users
        pass

    def change_user_type(self, userID: int, new_type: str) -> None:
        """
        Changes the user type of the specified user to the one provided
        """
        #TODO: Implement - change_user_type
        pass

    def delete_user(self, userID: int) -> None:
        """
        Deletes the provided user
        """
        #TODO: Implement - delete_user
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")