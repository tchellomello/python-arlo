"""The tests for the PyArlo platform."""
import unittest
from tests.common import load_fixture
import requests_mock

from pyarlo.const import (
    DEVICES_ENDPOINT, LIBRARY_ENDPOINT, LOGIN_ENDPOINT, RESET_ENDPOINT)

USERNAME = 'foo'
PASSWORD = 'bar'
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

        self.assertTrue(arlo.country_code, 'US')
        self.assertTrue(arlo.authenticated, 1498801924)
        self.assertTrue(arlo.userid, USERID)
        self.assertIsInstance(arlo.ArloMediaLibrary, ArloMediaLibrary)
        self.assertListEqual(arlo.ArloMediaLibrary.videos, [])

    @requests_mock.Mocker()
    def test_without_preload_devices(self, mock):
        """Test PyArlo without preloading videos but loading devices."""
        from pyarlo import PyArlo
        from pyarlo.camera import ArloCamera
        from pyarlo.base_station import ArloBaseStation

        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture('pyarlo_authentication.json'))
        mock.get(DEVICES_ENDPOINT,
                 text=load_fixture('pyarlo_devices.json'))

        arlo = PyArlo(USERNAME, PASSWORD, preload=False)

        arlo_devices = arlo.devices
        self.assertTrue(arlo_devices.get('base_station', arlo.base_stations))
        self.assertTrue(arlo_devices.get('cameras', arlo.cameras))

        cameras = arlo.cameras
        self.assertEquals(len(cameras), 2)
        for camera in cameras:
            self.assertIsNone(arlo.refresh_attributes(camera))
            self.assertIsInstance(camera, ArloCamera)
            self.assertTrue(camera.device_type, 'camera')
            self.assertTrue(camera.user_id, USERID)

            if camera.name == 'Front Door':
                self.assertTrue(camera.device_id, '48B14CAAAAAAA')

            if camera.name == 'Patio':
                self.assertTrue(camera.model_id, 'VMC3030')

        base = arlo.base_stations[0]
        self.assertIsInstance(base, ArloBaseStation)
        self.assertTrue(base.device_type, 'basestation')
        self.assertTrue(base.user_id, USERID)
        self.assertTrue(base.hw_version, 'VMB3010r2')
        self.assertIsNone(base.serial_number)

    @requests_mock.Mocker()
    def test_preload_devices(self, mock):
        """Test PyArlo preloading videos from the last day."""
        from pyarlo import PyArlo

        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture('pyarlo_authentication.json'))
        mock.get(DEVICES_ENDPOINT,
                 text=load_fixture('pyarlo_devices.json'))
        mock.post(LIBRARY_ENDPOINT,
                  text=load_fixture('pyarlo_videos.json'))

        arlo = PyArlo(USERNAME, PASSWORD, days=1)
        self.assertTrue(len(arlo.ArloMediaLibrary.videos), 3)

    @requests_mock.Mocker()
    def test_general_attributes(self, mock):
        """Test PyArlo without preloading videos."""
        from pyarlo import PyArlo
        from pyarlo.camera import ArloCamera

        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture('pyarlo_authentication.json'))
        mock.get(DEVICES_ENDPOINT,
                 text=load_fixture('pyarlo_devices.json'))
        mock.post(LIBRARY_ENDPOINT,
                  text=load_fixture('pyarlo_videos.json'))
        mock.get(RESET_ENDPOINT, json={'success': True})

        arlo = PyArlo(USERNAME, PASSWORD, days=1)

        self.assertEquals(arlo.__repr__(), '<PyArlo: 999-123456>')
        self.assertIsInstance(arlo.lookup_camera_by_id('48B14CAAAAAAA'),
                              ArloCamera)
        self.assertRaises(IndexError, arlo.lookup_camera_by_id, 'FAKEID')
        self.assertTrue(arlo.is_connected)
        self.assertTrue(arlo.unseen_videos_reset)
        self.assertIsNone(arlo.update())
