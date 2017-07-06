"""The tests for the PyArlo utils methods."""
import unittest
import mock

from tests.common import load_fixture

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

    @requests_mock.Mocker()
    @mock.patch('pyarlo.utils.http_get.open', create=True)
    def test_http_get_with_filename(self, mock, mock_open):
        """Test http_get with filename."""
        from pyarlo.utils import http_get

        mock.get(DEVICES_ENDPOINT,
                 text=load_fixture('pyarlo_devices.json'))
        self.assertTrue(http_get(DEVICES_ENDPOINT, filename="test_file"))

    @mock.patch('requests.get')
    def test_http_stream(self, mock):
        """Test http_stream."""
        from pyarlo.utils import http_stream
        import types

        self.assertIsInstance(http_stream(DEVICES_ENDPOINT),
                              types.GeneratorType)
