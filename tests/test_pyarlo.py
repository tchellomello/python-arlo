"""The tests for the PyArlo platform."""
import unittest
from tests.common import load_fixture
import requests_mock

from pyarlo.const import (
    LOGIN_ENDPOINT)

USERNAME = 'foo'
PASSWORD = 'bar'
EMAIL = 'foobar@mock-example.com'
COUNTRY_CODE = 'US'
TOKEN = '999999999999'
USERID = '999-123456'


class TestPyArlo(unittest.TestCase):
    """Tests for PyArlo component."""

    @requests_mock.Mocker()
    def test_without_preload(self, mock):
        """Test PyArlo without preloading videos."""
        from pyarlo import PyArlo
        from pyarlo.media import ArloMediaLibrary

        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture('pyarlo_authentication.json'))
        arlo = PyArlo(USERNAME, PASSWORD, preload=False)
        self.assertTrue(arlo.country_code, COUNTRY_CODE)
        self.assertTrue(arlo.authenticated, 1498801924)
        self.assertTrue(arlo.userid, USERID)
        self.assertIsInstance(arlo.ArloMediaLibrary, ArloMediaLibrary)
        self.assertListEqual(arlo.ArloMediaLibrary.videos, [])
