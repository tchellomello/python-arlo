"""The tests for the PyArlo utils methods."""
import unittest
import mock
import io

import requests_mock
from pyarlo.const import DEVICES_ENDPOINT

MOCK_DATA = {'data': 'This is a test message'}


class TestPyarloUtils(unittest.TestCase):
    """Tests for pyarlo.utils methods."""

    @requests_mock.Mocker()
    def test_http_get_errno_500(self, mock):
        """Test http_get with error 500."""
        from pyarlo.utils import http_get

        mock.get(DEVICES_ENDPOINT, json=MOCK_DATA, status_code=204)
        self.assertFalse(http_get(DEVICES_ENDPOINT))

    @requests_mock.Mocker()
    def test_http_get_ok_200(self, mock):
        """Test http_get with code 200."""
        from pyarlo.utils import http_get

        mock.get(DEVICES_ENDPOINT, json=MOCK_DATA)
        self.assertIsInstance(http_get(DEVICES_ENDPOINT), bytes)

    @mock.patch('pyarlo.utils.http_get')
    @requests_mock.Mocker()
    def test_http_get_with_filename(self, mock, open_mock):
        """Test http_get with filename."""
        from pyarlo.utils import http_get

        mock.get(DEVICES_ENDPOINT, json=MOCK_DATA)
        mockfile = io.StringIO()
        self.assertTrue(http_get(DEVICES_ENDPOINT, filename=mockfile))
