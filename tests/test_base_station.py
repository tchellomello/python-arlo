"""The tests for the PyArlo platform."""
import unittest
from mock import Mock, patch
from pyarlo import ArloBaseStation, PyArlo
from tests.common import load_fixture

import json
import requests_mock

from pyarlo.const import (
    DEVICES_ENDPOINT, LIBRARY_ENDPOINT, LOGIN_ENDPOINT, NOTIFY_ENDPOINT,
    RESOURCES
)

USERNAME = "foo"
PASSWORD = "bar"
USERID = "999-123456"


class TestArloBaseStation(unittest.TestCase):
    """Tests for ArloBaseStation component."""

    def load_base_station(self, mock):
        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture("pyarlo_authentication.json"))
        mock.get(DEVICES_ENDPOINT, text=load_fixture("pyarlo_devices.json"))
        mock.post(LIBRARY_ENDPOINT, text=load_fixture("pyarlo_videos.json"))
        arlo = PyArlo(USERNAME, PASSWORD, days=1)
        return arlo.base_stations[0]

    def load_base_properties(self, *args, **kwargs):
        return json.loads(load_fixture("pyarlo_base_station_properties.json"))

    def load_camera_properties(self, *args, **kwargs):
        return json.loads(load_fixture("pyarlo_camera_properties.json"))

    def load_camera_rules(self, *args, **kwargs):
        return json.loads(load_fixture("pyarlo_camera_rules.json"))

    def load_camera_schedule(self, *args, **kwargs):
        return json.loads(load_fixture("pyarlo_camera_schedule.json"))

    @requests_mock.Mocker()
    def test_properties(self, mock):
        """Test ArloBaseStation properties."""
        base = self.load_base_station(mock)
        self.assertIsInstance(base, ArloBaseStation)
        self.assertTrue(base.__repr__().startswith("<ArloBaseStation:"))
        self.assertEqual(base.device_id, "48B14CBBBBBBB")
        self.assertEqual(base.device_type, "basestation")
        self.assertEqual(base.model_id, "VMB3010")
        self.assertEqual(base.hw_version, "VMB3010r2")
        self.assertEqual(base.timezone, "America/New_York")
        self.assertEqual(base.unique_id, "235-48B14CBBBBBBB")
        self.assertEqual(base.user_id, USERID)
        self.assertEqual(base.user_role, "ADMIN")
        self.assertEqual(base.xcloud_id, "1005-123-999999")

        self.assertEqual(set(base.available_resources), set(RESOURCES.keys()))

    @requests_mock.Mocker()
    def test_is_motion_detection_enabled(self, mock):
        """Test ArloBaseStation.is_motion_detection_enabled properties."""
        with patch.object(ArloBaseStation, 'mode') as mocked_mode:
            mocked_mode.__get__ = Mock(return_value='armed')
            base = self.load_base_station(mock)
            self.assertTrue(base.is_motion_detection_enabled)

        with patch.object(ArloBaseStation, 'mode') as mocked_mode:
            mocked_mode.__get__ = Mock(return_value='disarmed')
            base = self.load_base_station(mock)
            self.assertFalse(base.is_motion_detection_enabled)

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_base_properties)
    def test_get_properties(self, mock):
        """Test ArloBaseStation.get_basestation_properties."""
        base = self.load_base_station(mock)
        base_properties = base.get_basestation_properties
        mocked_properties = self.load_base_properties()
        self.assertEqual(base_properties, mocked_properties["properties"])

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_properties)
    def test_camera_properties(self, mock):
        """Test ArloBaseStation.get_camera_properties."""
        base = self.load_base_station(mock)
        camera_properties = base.get_camera_properties
        mocked_properties = self.load_camera_properties()
        self.assertEqual(camera_properties, mocked_properties["properties"])

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_properties)
    def test_battery_level(self, mock):
        """Test ArloBaseStation.get_camera_battery_level."""
        base = self.load_base_station(mock)
        self.assertEqual(base.get_camera_battery_level, {"SERIAL2": 95, "SERIAL1": 77})

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_properties)
    def test_signal_strength(self, mock):
        """Test ArloBaseStation.get_camera_signal_strength."""
        base = self.load_base_station(mock)
        self.assertEqual(base.get_camera_signal_strength, {"SERIAL2": 4, "SERIAL1": 3})

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_rules)
    def test_camera_rules(self, mock):
        """Test ArloBaseStation.get_camera_rules."""
        base = self.load_base_station(mock)
        camera_rules = base.get_camera_rules
        mocked_rules = self.load_camera_rules()
        self.assertEqual(camera_rules, mocked_rules["properties"])

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_schedule)
    def test_camera_schedule(self, mock):
        """Test ArloBaseStation.get_camera_schedule."""
        base = self.load_base_station(mock)
        camera_schedule = base.get_camera_schedule
        mocked_schedules = self.load_camera_schedule()
        self.assertEqual(camera_schedule, mocked_schedules["properties"])
