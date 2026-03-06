import unittest
import pyodbc

from backend import Backend

class TestBackend(unittest.TestCase):
    def test_connect_default(self):
        backend = Backend()
        assert type(backend._connection()) == pyodbc.Connection

    def test_connect_college(self):
        backend = Backend("COLLEGE")
        assert type(backend._connection()) == pyodbc.Connection

    def test_connect_personal(self):
        backend = Backend("PERSONAL")
        assert type(backend._connection()) == pyodbc.Connection
