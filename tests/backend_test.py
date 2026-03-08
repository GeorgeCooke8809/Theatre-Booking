import pyodbc
import pytest
import logging

from backend import Backend

class TestBackend():
    @pytest.fixture(autouse = True)
    def create_backend(self):
        self.backend = Backend("PERSONAL")

    def _connection(self):
        """
        An internal function used for the context manager to connect to the database.
        """
        logging.debug("Connecting to personal (local) database...")

        cs = (
                "Driver={ODBC Driver 18 for SQL Server};"
                "Server=(localdb)\\TheatreBooking;"
                "Database=TheatreBooking;"
                "Trusted_Connection=yes;"
            )

        logging.debug("Connected to database")

        return pyodbc.connect(cs)
    
    def _clear_databases(self):
        """
        An internal testing function used to clear all of the tables.
        """
        tables = ["TRUNCATE TABLE dbo.Users;",
                "TRUNCATE TABLE dbo.Bookings;",
                "TRUNCATE TABLE dbo.BookingSeats;",
                "TRUNCATE TABLE dbo.Performances;",
                "TRUNCATE TABLE dbo.PerformanceUnavailableSeats;",
                "TRUNCATE TABLE dbo.Showings;",
                ]

        with self._connection() as connection:
            cursor = connection.cursor()

            for command in tables:
                cursor.execute(command)

    def test_connect_default(self):
        assert type(self.backend._connection()) == pyodbc.Connection

    def test_get_next_id_users(self):
        assert type(self.backend._get_next_ID("Users")) == int

    def test_get_next_id_bookings(self):
        assert type(self.backend._get_next_ID("Users")) == int

    def test_get_next_id_booking_seats(self):
        assert type(self.backend._get_next_ID("BookingSeats")) == int

    def test_get_next_id_performances(self):
        assert type(self.backend._get_next_ID("Performances")) == int

    def test_get_next_id_performance_unavailable_seats(self):
        assert type(self.backend._get_next_ID("PerformanceUnavailableSeats")) == int

    def test_get_next_id_showings(self):
        assert type(self.backend._get_next_ID("Showings")) == int

    def test_add_user_valid_data(self):
        self._clear_databases()

        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend._get_next_ID("Users") == 2

    def test_add_multiple_users(self):
        self._clear_databases()

        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")
        self.backend.create_user("Olly", "Kitson", "ollynortheykitson@icloud.com", "07802 447089", "SuperPassword1234*")
        self.backend.create_user("Akil", "rameez", "25rameeza110@collyers.ac.uk", "07802 447089", "SuperPassword12345*")

        assert self.backend._get_next_ID("Users") == 4

    def test_add_same_email(self): # should fail
        self._clear_databases()

        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        with pytest.raises(Exception):
            self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

    def test_email_in_database_with_email_in_database(self):
        self._clear_databases()
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_email_in_database("25cookeg899@collyers.ac.uk") == True

    def test_email_in_database_with_email_not_in_database(self):
        self._clear_databases()
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_email_in_database("ksdhdglwuvg@gmail.com") == False

    def test_check_password_correct(self):
        self._clear_databases()
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_password(email="25cookeg899@collyers.ac.uk", password_attempt="SuperPassword123*") == True

    def test_check_password_incorrect(self):
        self._clear_databases()
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_password(email="25cookeg899@collyers.ac.uk", password_attempt="SuperPassword123") == False

    def test_check_password_empty_database(self):
        self._clear_databases()

        assert self.backend.check_password(email="25cookeg899@collyers.ac.uk", password_attempt="SuperPassword123") == False

    def test_check_password_no_email(self):
        self._clear_databases()
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_password(email="25cookeg89@collyers.ac.uk", password_attempt="SuperPassword123") == False