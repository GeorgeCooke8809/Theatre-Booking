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
            backend._get_next_ID("HHHH") # TODO: make pass if fail