import pyodbc
import pytest
import logging

from backend import Backend

class TestBackend():
    @pytest.fixture(autouse = True)
    def create_backend(self):
        self.backend = Backend("PERSONAL")
        self._clear_databases()

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
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend._get_next_ID("Users") == 2

    def test_add_multiple_users(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")
        self.backend.create_user("Olly", "Kitson", "ollynortheykitson@icloud.com", "07802 447089", "SuperPassword1234*")
        self.backend.create_user("Akil", "Rameez", "25rameeza110@collyers.ac.uk", "07802 447089", "SuperPassword12345*")

        assert self.backend._get_next_ID("Users") == 4

    def test_add_same_email(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        with pytest.raises(Exception):
            self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

    def test_email_in_database_with_email_in_database(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_email_in_database("25cookeg899@collyers.ac.uk") == True

    def test_email_in_database_with_email_not_in_database(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_email_in_database("ksdhdglwuvg@gmail.com") == False

    def test_check_password_correct(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_password(email="25cookeg899@collyers.ac.uk", password_attempt="SuperPassword123*") == True

    def test_check_password_incorrect(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_password(email="25cookeg899@collyers.ac.uk", password_attempt="SuperPassword123") == False

    def test_check_password_empty_database(self):
        assert self.backend.check_password(email="25cookeg899@collyers.ac.uk", password_attempt="SuperPassword123") == False

    def test_check_password_no_email(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_password(email="25cookeg89@collyers.ac.uk", password_attempt="SuperPassword123") == False

    def test_add_performance_valid(self):
        assert self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0) == 1
        assert self.backend._get_next_ID("Performances") == 2

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (1))
            values = cursor.fetchone()

            assert float(values[0]) == 5
            assert float(values[1]) == 10
            assert float(values[2]) == 5

    def test_add_performances_default_prices(self):
        assert self.backend.add_performance("Lorem Ipsum", "This is a super duper description") == 1
        assert self.backend._get_next_ID("Performances") == 2

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (1))
            values = cursor.fetchone()

            assert float(values[0]) == 5
            assert float(values[1]) == 10
            assert float(values[2]) == 5

    def test_add_performance_decimal_prices(self):
        assert self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 7.4, 15, 2.5) == 1
        assert self.backend._get_next_ID("Performances") == 2

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (1))
            values = cursor.fetchone()

            assert float(values[0]) == 7.4
            assert float(values[1]) == 15
            assert float(values[2]) == 2.5

    def test_add_performance_large_numbers_no_decimal(self):
        assert self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 250, 1500, 750) == 1
        assert self.backend._get_next_ID("Performances") == 2

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (1))
            values = cursor.fetchone()

            assert float(values[0]) == 250
            assert float(values[1]) == 1500
            assert float(values[2]) == 750

    def test_add_performance_large_numbers_decimal(self):
        assert self.backend.add_performance("Lorem Ipsumm", "lThis is a super duper description", 249.99, 1499.99, 749.99) == 1
        assert self.backend._get_next_ID("Performances") == 2

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (1))
            values = cursor.fetchone()

            assert float(values[0]) == 249.99
            assert float(values[1]) == 1499.99
            assert float(values[2]) == 749.99

    def test_add_performance_too_many_decimals_child(self):
        with pytest.raises(Exception):
            self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 249.999, 1499.99, 749.99)

    def test_add_performance_too_many_decimals_adult(self):
        with pytest.raises(Exception):
            self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 249.99, 1499.999, 749.99)

    def test_add_performance_too_many_decimals_elderly(self):
        with pytest.raises(Exception):
            self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 249.99, 1499.99, 749.999)

    def test_add_performance_too_many_digits_before_decimal_child(self):
        with pytest.raises(Exception):
            self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 100_249.99, 1499.99, 749.99)

    def test_add_performance_too_many_digits_before_decimal_adult(self):
        with pytest.raises(Exception):
            self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 249.99, 100_1499.99, 749.99)

    def test_add_performance_too_many_digits_before_decimal_elderly(self):
        with pytest.raises(Exception):
            self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 249.99, 1499.99, 100_749.99)

    def test_add_performances_multiple(self):
        assert self.backend.add_performance("Lorem Ipsum", "This is a super duper description") == 1
        assert self.backend.add_performance("Lorem Ipsumm", "This is a super duper description", 7.6, 15, 2.5) == 2
        assert self.backend._get_next_ID("Performances") == 3

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (1))
            values = cursor.fetchone()

            assert float(values[0]) == 5
            assert float(values[1]) == 10
            assert float(values[2]) == 5

            cursor.execute("SELECT childPrice, adultPrice, elderlyPrice FROM dbo.Performances WHERE performanceID = ?", (2))
            values = cursor.fetchone()

            assert float(values[0]) == 7.6
            assert float(values[1]) == 15
            assert float(values[2]) == 2.5