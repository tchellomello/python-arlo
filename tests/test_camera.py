"""The tests for the PyArlo camera class."""
import unittest
from tests.common import load_fixture
import requests_mock

from pyarlo.const import (
    DEVICES_ENDPOINT, LIBRARY_ENDPOINT, LOGIN_ENDPOINT,
    RESET_CAM_ENDPOINT)

USERNAME = 'foo'
PASSWORD = 'bar'
USERID = '999-123456'

MOCK_DATA = {'success': True}


class TestArloCamera(unittest.TestCase):
    """Tests for ArloCamera component."""

    @requests_mock.Mocker()
    def test_camera_attributes(self, mock):
        """Test ArloCamera attributes."""
        from pyarlo import PyArlo
        from pyarlo.camera import ArloCamera

        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture('pyarlo_authentication.json'))
        mock.get(DEVICES_ENDPOINT,
                 text=load_fixture('pyarlo_devices.json'))
        mock.post(LIBRARY_ENDPOINT,
                  text=load_fixture('pyarlo_videos.json'))

        arlo = PyArlo(USERNAME, PASSWORD, preload=False)

        arlo_devices = arlo.devices
        self.assertTrue(arlo_devices.get('cameras', arlo.cameras))

        cameras = arlo.cameras
        self.assertEqual(len(cameras), 2)
        for camera in cameras:
            self.assertTrue(camera.__repr__().startswith('<ArloCamera:'))
            self.assertIsNone(arlo.refresh_attributes(camera))
            self.assertIsInstance(camera, ArloCamera)
            self.assertTrue(camera.device_type, 'camera')
            self.assertTrue(camera.user_id, USERID)
            self.assertEqual(camera.hw_version, 'H7')
            self.assertEqual(camera.timezone, 'America/New_York')
            self.assertEqual(camera.user_role, 'ADMIN')
            self.assertTrue(len(camera.captured_today), 1)

            if camera.name == 'Front Door':
                self.assertTrue(camera.device_id, '48B14CAAAAAAA')
                self.assertEqual(camera.unique_id, '235-48B14CAAAAAAA')
                self.assertEquals(camera.unseen_videos, 39)
                self.assertEqual(camera.xcloud_id, '1005-123-999999')

                # unseen videos
                mock_url = RESET_CAM_ENDPOINT.format(camera.unique_id)
                mock.get(mock_url, json=MOCK_DATA)
                self.assertTrue(camera.unseen_videos_reset)

            if camera.name == 'Patio':
                self.assertTrue(camera.model_id, 'VMC3030')
                self.assertEqual(camera.unique_id, '999-123456_48B14C1299999')
                self.assertEquals(camera.unseen_videos, 233)

                # unseen videos
                mock_url = RESET_CAM_ENDPOINT.format(camera.unique_id)
                mock.get(mock_url, json=MOCK_DATA)
                self.assertTrue(camera.unseen_videos_reset)
