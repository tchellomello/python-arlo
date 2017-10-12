"""The tests for the PyArlo camera class."""
import requests_mock
import unittest

from tests.common import (
    load_fixture,
    load_fixture_json,
    load_camera_live_streaming,
    load_camera_properties as load_camera_props,
    open_fixture
)

from mock import patch
from pyarlo import PyArlo, ArloBaseStation
from pyarlo.camera import ArloCamera
from pyarlo.const import (
    DEVICES_ENDPOINT, LIBRARY_ENDPOINT, LOGIN_ENDPOINT,
    NOTIFY_ENDPOINT, RESET_CAM_ENDPOINT, STREAM_ENDPOINT,
    UNSUBSCRIBE_ENDPOINT
)

BASE_STATION_ID = "48B14CBBBBBBB"
USERNAME = "foo"
PASSWORD = "bar"
USERID = "999-123456"

MOCK_DATA = {"success": True}


class TestArloCamera(unittest.TestCase):
    """Tests for ArloCamera component."""

    def load_arlo(self, mock):
        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture("pyarlo_authentication.json"))
        mock.get(DEVICES_ENDPOINT, text=load_fixture("pyarlo_devices.json"))
        mock.post(LIBRARY_ENDPOINT, text=load_fixture("pyarlo_videos.json"))
        mock.post(NOTIFY_ENDPOINT.format(BASE_STATION_ID),
                  text=load_fixture("pyarlo_camera_properties.json"))
        mock.get(UNSUBSCRIBE_ENDPOINT)
        return PyArlo(USERNAME, PASSWORD, preload=False)

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_props)
    def test_camera_properties(self, mock):
        """Test ArloCamera properties."""
        arlo = self.load_arlo(mock)
        cameras = arlo.cameras
        basestation = arlo.base_stations[0]
        basestation.update()
        self.assertEqual(len(cameras), 2)
        for camera in cameras:
            camera.update()
            self.assertTrue(camera.__repr__().startswith("<ArloCamera:"))
            self.assertIsNone(arlo.refresh_attributes(camera))
            self.assertIsInstance(camera, ArloCamera)
            self.assertTrue(camera.device_type, "camera")
            self.assertTrue(camera.user_id, USERID)
            self.assertEqual(camera.hw_version, "H7")
            self.assertEqual(camera.timezone, "America/New_York")
            self.assertEqual(camera.user_role, "ADMIN")
            self.assertTrue(len(camera.captured_today), 1)
            self.assertIsNotNone(camera.properties)

            if camera.name == "Front Door":
                self.assertTrue(camera.device_id, "48B14CAAAAAAA")
                self.assertEqual(camera.unique_id, "235-48B14CAAAAAAA")
                self.assertEqual(camera.unseen_videos, 39)
                self.assertEqual(camera.xcloud_id, "1005-123-999999")
                self.assertEqual(camera.serial_number, camera.device_id)

                self.assertEqual(camera.get_battery_level, 77)
                self.assertEqual(camera.get_signal_strength, 3)
                self.assertEqual(camera.get_brightness, 0)
                self.assertEqual(camera.get_mirror_state, 0)
                self.assertEqual(camera.get_flip_state, 0)
                self.assertEqual(camera.get_powersave_mode, 2)
                self.assertTrue(camera.is_camera_connected)
                self.assertEqual(camera.get_motion_detection_sensitivity, 80)

                image_url = camera._attrs.get("presignedLastImageUrl")

                response_body = open_fixture("last_image.jpg", binary=True)
                mock.get(image_url, body=response_body)
                self.assertEqual(
                    camera.last_image,
                    load_fixture("last_image.jpg", binary=True)
                )

                videos = load_fixture_json("pyarlo_videos.json")
                last_video_url = videos["data"][-1]["presignedContentUrl"]
                self.assertEqual(camera.last_video.video_url, last_video_url)

            if camera.name == "Patio":
                self.assertTrue(camera.model_id, "VMC3030")
                self.assertEqual(camera.unique_id, "999-123456_48B14C1299999")
                self.assertEqual(camera.unseen_videos, 233)

    @requests_mock.Mocker()
    def test_unseen_videos_reset(self, mock):
        """Test ArloCamera.unseen_videos_reset."""
        arlo = self.load_arlo(mock)
        camera = arlo.cameras[0]

        reset_url = RESET_CAM_ENDPOINT.format(camera.unique_id)
        mock.get(reset_url, json=MOCK_DATA)
        self.assertTrue(camera.unseen_videos_reset)

        camera.unseen_videos_reset()
        request = mock.request_history[2]
        self.assertEqual(
            "{}://{}{}?{}".format(
                request.scheme, request.netloc, request.path, request.query
            ).lower(),
            reset_url.lower()
        )

    @requests_mock.Mocker()
    def test_videos(self, mock):
        """Test ArloCamera.videos."""
        arlo = self.load_arlo(mock)
        camera = arlo.cameras[0]
        videos = camera.videos(days=10000)
        self.assertEqual(len(videos), 1)

    @requests_mock.Mocker()
    def test_play_last_video(self, mock):
        """Test ArloCamera.play_last_video."""
        arlo = self.load_arlo(mock)
        camera = arlo.cameras[0]
        last_video_url = camera.last_video.video_url
        response_body = open_fixture("last_image.jpg", binary=True)
        mock.get(last_video_url, body=response_body)
        video = camera.play_last_video()
        self.assertTrue(video)

    @requests_mock.Mocker()
    def test_live_streaming(self, mock):
        """Test ArloCamera.live_streaming."""
        arlo = self.load_arlo(mock)
        camera = arlo.cameras[0]
        response_text = load_fixture("pyarlo_camera_live_streaming.json")
        mock.post(STREAM_ENDPOINT, text=response_text)
        mocked_streaming_response = load_camera_live_streaming()
        streaming_url = camera.live_streaming()
        self.assertEqual(
            streaming_url, mocked_streaming_response["data"]["url"]
        )
