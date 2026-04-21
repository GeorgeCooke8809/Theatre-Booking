from backend_test import Test
import pytest
import logging
import pyodbc
from backend import Backend

class TestDeletePerformance(Test):
    def test_delete_performance_valid_no_extras(self):
        self.backend.add_performance("Lorem Ipsum", "This is a super duper description", 5.0, 10.0, 5.0)

        self.backend.delete_performance(1)