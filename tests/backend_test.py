import pyodbc
import pytest
import logging
from datetime import date

from backend import Backend

class Test: # parent class to all test classes with regularly repeated code
    @pytest.fixture(autouse = True)
    def create_backend(self):
        """
        Code ran before every test to create backend connection and clear tables
        """
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

class TestConnect(Test):
    def test_connect_default(self):
        assert type(self.backend._connection()) == pyodbc.Connection

class TestGetNextID(Test):
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

class TestAddUser(Test):
    def test_add_user_valid_data(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend._get_next_ID("Users") == 2

    def test_add_multiple_users(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")
        self.backend.create_user("Olly", "Kitson", "ollynortheykitson@icloud.com", "07802 447089", "SuperPassword1234*")
        self.backend.create_user("Akil", "Rameez", "25rameeza110@collyers.ac.uk", "07802 447089", "SuperPassword12345*")

        assert self.backend._get_next_ID("Users") == 4

    def test_add_user_same_email(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        with pytest.raises(Exception):
            self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

class TestEmailInDatabase(Test):
    def test_email_in_database_with_email_in_database(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_email_in_database("25cookeg899@collyers.ac.uk") == True

    def test_email_in_database_with_email_not_in_database(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_email_in_database("ksdhdglwuvg@gmail.com") == False

class TestCheckPassword(Test):
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

class TestAddPerformance(Test):
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

class TestPerformanceExists(Test):
    def test_performance_exists_with_valid(self):
        performanceID = self.backend.add_performance("Lorem Ipsum", "This is a super duper description")

        assert self.backend._check_performance_exists(performanceID) == True

    def test_performance_exists_with_invalid(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description")
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description")
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description")
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description")

        assert self.backend._check_performance_exists(66) == False

class TestAddShowing(Test):
    def test_add_showing_valid(self):
        performanceID = self.backend.add_performance("Lorem Ipsum", "This is a super duper description")

        assert self.backend.add_showing(performanceID, date(2026, 3, 9)) == 1

    def test_add_showing_performance_does_not_exist(self):
        with pytest.raises(Exception):
            self.backend.add_showing(1, date(2026, 3, 9))

    def test_add_showing_not_date_format(self):
        performanceID = self.backend.add_performance("Lorem Ipsum", "This is a super duper description")

        with pytest.raises(Exception):
            self.backend.add_showing(performanceID, "2026/03/09")

class TestGetAllUsers(Test):
    def test_get_all_users(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")
        self.backend.create_user("Olly", "Kitson", "ollynortheykitson@icloud.com", "07802 447089", "SuperPassword1234*")
        self.backend.create_user("Akil", "Rameez", "25rameeza110@collyers.ac.uk", "07802 447089", "SuperPassword12345*")

        users = self.backend.get_all_users()

        assert len(users) == 3
        assert type(users) == list
        assert type(users[0]) == tuple

        assert users[0] == (1, "George", "Cooke", "07802 447089", "VISITOR")

class TestUserExists(Test):
    def test_check_user_exists_valid(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend._check_user_exists(1) == True

    def test_check_user_exists_invalid(self):
        assert self.backend._check_user_exists(1) == False

class TestChangeUserType(Test):
    def test_change_user_type_ADMIN(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        self.backend.change_user_type(1, "ADMIN")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT userType FROM dbo.Users WHERE userID = ?", (1))
            userType = cursor.fetchone()[0]

        assert userType == "ADMIN"

    def test_change_user_type_SPECIAL(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        self.backend.change_user_type(1, "SPECIAL")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT userType FROM dbo.Users WHERE userID = ?", (1))
            userType = cursor.fetchone()[0]

        assert userType == "SPECIAL"

    def test_change_user_type_VISITOR(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        self.backend.change_user_type(1, "SPECIAL")
        self.backend.change_user_type(1, "VISITOR")

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT userType FROM dbo.Users WHERE userID = ?", (1))
            userType = cursor.fetchone()[0]

        assert userType == "VISITOR"

    def test_change_user_type_invalid_type(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        with pytest.raises(Exception):
            self.backend.change_user_type(1, "GUEST")

    def test_change_user_type_invalid_ID(self):
        with pytest.raises(Exception):
            self.backend.change_user_type(1, "ADMIN")

class TestDeleteUser(Test):
    def test_delete_user_valid(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        self.backend.delete_user(1)

        assert len(self.backend.get_all_users()) == 0

    def test_delete_user_invalid(self):
        with pytest.raises(Exception):
            self.backend.delete_user(1)

class TestCheckUserAdmin(Test):
    def test_check_user_admin_true_valid(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")
        self.backend.change_user_type(1, "ADMIN")

        assert self.backend.check_user_admin(1) == True

    def test_check_user_admin_visitor_valid(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        assert self.backend.check_user_admin(1) == False

    def test_check_user_admin_special_valid(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")
        self.backend.change_user_type(1, "SPECIAL")

        assert self.backend.check_user_admin(1) == False

    def test_check_user_admin_invalid_user(self):
        with pytest.raises(Exception):
            self.backend.check_user_admin(1)

class TestGetBookingPrice(Test):
    def test_get_booking_price_special_valid(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")
        self.backend.change_user_type(1, "SPECIAL")

        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        assert self.backend.get_booking_price(1, 1, 5, 5, 5) == "£0.00"

    def test_get_booking_price_visitor_valid(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        assert self.backend.get_booking_price(1, 1, 5, 5, 5) == "£100.00"

    def test_get_booking_price_admin_valid(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")
        self.backend.change_user_type(1, "ADMIN")

        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        assert self.backend.get_booking_price(1, 1, 5, 5, 5) == "£100.00"

    def test_get_booking_price_invalid_userID(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        with pytest.raises(Exception):
            assert self.backend.get_booking_price(userID=1, performanceID=1, no_child_seats=5, no_adult_seats=5, no_elderly_seats=5) == "£100.00"

    def test_get_booking_price_invalid_performanceID(self):
        self.backend.create_user("George", "Cooke", "25cookeg899@collyers.ac.uk", "07802 447089", "SuperPassword123*")

        with pytest.raises(Exception):
            assert self.backend.get_booking_price(userID=1, performanceID=1, no_child_seats=5, no_adult_seats=5, no_elderly_seats=5) == "£100.00"

class TestCheckSeatIDValid(Test):
    def test_check_seat_ID_valid_valid(self):
        assert self.backend._check_valid_seat_ID("1D") == True

    def test_check_seat_ID_valid_boundary(self):
        assert self.backend._check_valid_seat_ID("10T") == True

    def test_check_seat_ID_valid_number_invalid(self):
        assert self.backend._check_valid_seat_ID("11B") == False

    def test_check_seat_ID_valid_number_invalid_negative(self):
        assert self.backend._check_valid_seat_ID("-1B") == False

    def test_check_seat_ID_valid_letter_invalid(self):
        assert self.backend._check_valid_seat_ID("5U") == False

    def test_check_seat_ID_valid_number_not_numeric(self):
        assert self.backend._check_valid_seat_ID("5CU") == False

    def test_check_seat_ID_valid_letter_is_number(self):
        assert self.backend._check_valid_seat_ID("91") == False

class TestMarkSeatUnavailable(Test):
    def test_mark_seat_unavailable_valid(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.mark_seat_unavailable("1B", 1)

    def test_mark_seat_unavailable_multiple_valid(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        for seat in ["1A", "1B", "1C", "5H", "10T"]:
            self.backend.mark_seat_unavailable(seat, 1)

    def test_mark_seat_unavailable_invalid_seatID_number(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        with pytest.raises(Exception):
            self.backend.mark_seat_unavailable("11B", 1)

    def test_mark_seat_unavailable_invalid_seatID_letter(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        with pytest.raises(Exception):
            self.backend.mark_seat_unavailable("5U", 1)

    def test_mark_seat_unavailable_invalid_performanceID(self):
        with pytest.raises(Exception):
            self.backend.mark_seat_unavailable("5B", 1)

    def test_mark_seat_unavailable_invalid_seatID_number_negative(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        with pytest.raises(Exception):
            self.backend.mark_seat_unavailable("-1B", 1)

class TestCheckShowingExists(Test):
    def test_check_showing_exists_valid_true(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1, date(2026, 3, 10))

        assert self.backend._check_showing_exists(1) == True

    def test_check_showing_exists_valid_false(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1, date(2026, 3, 10))

        assert self.backend._check_showing_exists(2) == False

    def test_check_showing_exists_letter_showing_ID(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1, date(2026, 3, 10))

        with pytest.raises(Exception):
            self.backend._check_showing_exists("ABC") == False

class TestGetUnavailableSeats(Test):
    # TODO: test with bookings added
    def test_get_unavailable_seats_valid(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1, date(2026, 3, 10))

        for seat in ["1A", "1B", "1C", "5H", "10T"]:
            self.backend.mark_seat_unavailable(seat, 1)

        assert self.backend.get_unavailable_seats(1) == ["1A", "1B", "1C", "5H", "10T"]

    def test_get_unavailable_seats_showing_does_not_exist(self):
        with pytest.raises(Exception):
            self.backend.get_unavailable_seats(1)

    def test_get_unavailable_seats_all_available(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1, date(2026, 3, 10))

        assert self.backend.get_unavailable_seats(1) == []

class TestCheckSeatAvailable(Test):
    #TODO: test with bookings

    def test_check_seat_available_valid_marked_unavailable_true(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1, date(2026, 3, 10))

        assert self.backend._check_seat_available("7G", 1) == True

    def test_check_seat_available_valid_marked_unavailable_false(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1, date(2026, 3, 10))

        for seat in ["1A", "1B", "1C", "5H", "10T"]:
            self.backend.mark_seat_unavailable(seat, 1)

        assert self.backend._check_seat_available("1A", 1) == False
        assert self.backend._check_seat_available("1B", 1) == False
        assert self.backend._check_seat_available("1C", 1) == False
        assert self.backend._check_seat_available("5H", 1) == False
        assert self.backend._check_seat_available("10T", 1) == False

    def test_check_seat_available_invalid_showing(self):
        with pytest.raises(Exception):
            self.backend._check_seat_available("1A", 1)

    def test_check_seat_available_invalid_seat(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1, date(2026, 3, 10))

        with pytest.raises(Exception):
            self.backend._check_seat_available("11A", 1)