"""The tests for the PyArlo Media component."""
import unittest
from tests.common import load_fixture
import requests_mock

from pyarlo.const import (
    DEVICES_ENDPOINT, LIBRARY_ENDPOINT, LOGIN_ENDPOINT)

USERNAME = 'foo'
PASSWORD = 'bar'


class TestArloVideo(unittest.TestCase):
    """Tests for ArloVideo component."""

    @requests_mock.Mocker()
    def test_load_method(self, mock):
        """Test PyArlo ArloMediaLibrary.load() method."""
        from pyarlo import PyArlo
        from pyarlo.camera import ArloCamera

        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture('pyarlo_authentication.json'))
        mock.get(DEVICES_ENDPOINT, text=load_fixture('pyarlo_devices.json'))
        mock.post(LIBRARY_ENDPOINT, text=load_fixture('pyarlo_videos.json'))

        arlo = PyArlo(USERNAME, PASSWORD, days=1)

        for video in arlo.ArloMediaLibrary.videos:
            self.assertTrue(video.id, video.created_at)
            self.assertEqual(video.content_type, 'video/mp4')
            self.assertIsInstance(video.camera, ArloCamera)
            self.assertGreaterEqual(video.media_duration_seconds, 45)
            self.assertEqual(video.triggered_by, 'motionRecord')
            self.assertTrue(video.thumbnail_url.startswith('https://'))
            self.assertTrue(video.video_url.startswith('https://'))

            if video.id == '1498880152142':
                vstr = '<ArloVideo: Patio Fri-06_30_17:23:35:52 00:01:00>'
                self.assertEqual(video.__repr__(), vstr)
