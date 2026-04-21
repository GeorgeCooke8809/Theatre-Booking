from backend_test import Test
import pytest
import logging
import pyodbc
from backend import Backend

class TestGetBookingPrice(Test):
    def test_get_booking_price_valid(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)
        self.backend.add_showing(1)
        self.backend.create_user("George", "Cooke", "georgecooke8809@gmail.com", "07802447080", "GreatPassword")

        assert self.backend.get_booking_price(1, 1, 1, 1, 1) == "£20.00"