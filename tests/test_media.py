"""The tests for the PyArlo Media component."""
import unittest
from tests.common import load_fixture
import requests_mock

from pyarlo.const import (
    DEVICES_ENDPOINT, LIBRARY_ENDPOINT, LOGIN_ENDPOINT)

USERNAME = 'foo'
PASSWORD = 'bar'
USERID = '999-123456'


class TestArloMediaLibrary(unittest.TestCase):
    """Tests for ArloMediaLibrary component."""

    @requests_mock.Mocker()
    def test_arlo_media_library(self, mock):
        """Test PyArlo MediaLibrary tests."""
        from pyarlo import PyArlo

        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture('pyarlo_authentication.json'))
        mock.post(LIBRARY_ENDPOINT,
                  text=load_fixture('pyarlo_videos.json'))

        arlo = PyArlo(USERNAME, PASSWORD, preload=False)
        self.assertEquals(arlo.ArloMediaLibrary.__repr__(),
                          '<ArloMediaLibrary: 999-123456>')

    @requests_mock.Mocker()
    def test_load_method(self, mock):
        """Test PyArlo ArloMediaLibrary.load() method."""
        from pyarlo import PyArlo
        from pyarlo.media import ArloMediaLibrary

        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture('pyarlo_authentication.json'))
        mock.get(DEVICES_ENDPOINT,
                 text=load_fixture('pyarlo_devices.json'))
        mock.post(LIBRARY_ENDPOINT,
                  text=load_fixture('pyarlo_videos.json'))

        arlo = PyArlo(USERNAME, PASSWORD, preload=False)
        library = ArloMediaLibrary(arlo, preload=False)
        videos = library.load(days=1,
                              only_cameras=[
                                arlo.lookup_camera_by_id('48B14C1299999')])
        self.assertEquals(len(videos), 2)
