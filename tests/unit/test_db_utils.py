"""module contains test for db_utils"""

from unittest import TestCase
from unittest import mock
from types import SimpleNamespace

import pytest

import gn3
from gn3.db_utils import database_connector
from gn3.db_utils import parse_db_url

@pytest.fixture(scope="class")
def setup_app(request, fxtr_app):
    """Setup the fixtures for the class."""
    request.cls.app = fxtr_app

class TestDatabase(TestCase):
    """class contains testd for db connection functions"""

    @pytest.mark.unit_test
    @mock.patch("gn3.db_utils.mdb")
    @mock.patch("gn3.db_utils.parse_db_url")
    def test_database_connector(self, mock_db_parser, mock_sql):
        """test for creating database connection"""
        mock_db_parser.return_value = ("localhost", "guest", "4321", "users", None)
        callable_cursor = lambda: SimpleNamespace(execute=3)
        cursor_object = SimpleNamespace(cursor=callable_cursor)
        mock_sql.connect.return_value = cursor_object
        mock_sql.close.return_value = None
        results = database_connector()

        mock_sql.connect.assert_called_with(
            "localhost", "guest", "4321", "users", port=3306)
        self.assertIsInstance(
            results, SimpleNamespace, "database not created successfully")

    @pytest.mark.unit_test
    @pytest.mark.usefixtures("setup_app")
    def test_parse_db_url(self):
        """test for parsing db_uri env variable"""
        print(self.__dict__)
        with self.app.app_context(), mock.patch.dict(# pylint: disable=[no-member]
                gn3.db_utils.current_app.config,
                {"SQL_URI": "mysql://username:4321@localhost/test"},
                clear=True):
            results = parse_db_url()
            expected_results = ("localhost", "username", "4321", "test", None)
            self.assertEqual(results, expected_results)
