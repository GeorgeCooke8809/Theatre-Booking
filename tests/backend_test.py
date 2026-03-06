import pyodbc
import logging
import pytest

from backend import Backend

logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

class TestBackend():
    def test_connect_default(self):
        backend = Backend()
        assert type(backend._connection()) == pyodbc.Connection

    def test_connect_college(self):
        backend = Backend("COLLEGE")
        assert type(backend._connection()) == pyodbc.Connection

    def test_connect_personal(self):
        backend = Backend("PERSONAL")
        assert type(backend._connection()) == pyodbc.Connection

    def test_get_next_id_invalid_table(self):
        backend = Backend("PERSONAL")
        with pytest.raises(Exception):
            backend._get_next_ID("HHHH")

    def test_get_next_id_users(self):
        backend = Backend("PERSONAL")
        assert type(backend._get_next_ID("Users")) == int

    def test_get_next_id_bookings(self):
        backend = Backend("PERSONAL")
        assert type(backend._get_next_ID("Users")) == int

    def test_get_next_id_booking_seats(self):
        backend = Backend("PERSONAL")
        assert type(backend._get_next_ID("BookingSeats")) == int

    def test_get_next_id_performances(self):
        backend = Backend("PERSONAL")
        assert type(backend._get_next_ID("Performances")) == int

    def test_get_next_id_performance_unavailable_seats(self):
        backend = Backend("PERSONAL")
        assert type(backend._get_next_ID("PerformanceUnavailableSeats")) == int

    def test_get_next_id_showings(self):
        backend = Backend("PERSONAL")
        assert type(backend._get_next_ID("Showings")) == int

    def test_email_in_database_with_email_in_database(self):
        backend = Backend("PERSONAL")
        assert backend.check_email_in_database("25cookeg899@collyers.ac.uk") == True

    def test_email_in_database_with_email_not_in_database(self):
        backend = Backend("PERSONAL")
        assert backend.check_email_in_database("ksdhdglwuvg@gmail.com") == False