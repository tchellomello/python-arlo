"""The tests for the PyArlo platform."""
import unittest
from mock import patch
from pyarlo import ArloBaseStation, PyArlo
from tests.common import load_fixture

import json
import requests_mock

from pyarlo.const import (
    DEVICES_ENDPOINT, LIBRARY_ENDPOINT, LOGIN_ENDPOINT, NOTIFY_ENDPOINT)

USERNAME = "foo"
PASSWORD = "bar"
USERID = "999-123456"


class TestArloBaseStationModes(unittest.TestCase):
    """Tests for ArloBaseStation component modes."""

    def load_modes(self, *args, **kwargs):
        return json.loads(load_fixture("pyarlo_modes.json"))

    def load_base_station(self, mock):
        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture("pyarlo_authentication.json"))
        mock.get(DEVICES_ENDPOINT, text=load_fixture("pyarlo_devices.json"))
        mock.post(LIBRARY_ENDPOINT, text=load_fixture("pyarlo_videos.json"))
        arlo = PyArlo(USERNAME, PASSWORD, days=1)
        return arlo.base_stations[0]

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_modes)
    def test_current_mode(self, mock):
        """Test PyArlo BaseStation.mode property."""
        base_station = self.load_base_station(mock)
        self.assertEqual(base_station.mode, "disarmed")

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_modes)
    def test_get_available_modes(self, mock):
        """Test PyArlo BaseStation.get_available_modes method."""
        base_station = self.load_base_station(mock)
        available_modes = base_station.get_available_modes()
        mocked_modes = self.load_modes()
        self.assertEqual(available_modes, mocked_modes["properties"]["modes"])

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_modes)
    def test_available_modes_with_ids(self, mock):
        """Test PyArlo BaseStation.available_modes_with_ids property."""
        base_station = self.load_base_station(mock)
        available_modes = base_station.available_modes_with_ids
        self.assertEqual(
            available_modes,
            {
                "schedule": "true",
                "disarmed": "mode0",
                "armed": "mode1",
                "Inside": "mode3",
                "Home": "mode4"
            }
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_modes)
    def test_available_modes(self, mock):
        """Test PyArlo BaseStation.available_modes property."""
        base_station = self.load_base_station(mock)
        available_modes = base_station.available_modes
        self.assertEqual(
            set(available_modes),
            set(["Home", "Inside", "armed", "disarmed", "schedule"])
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_modes)
    def test_set_mode(self, mock):
        """Test PyArlo BaseStation.mode property."""
        notify_url = NOTIFY_ENDPOINT.format("48b14cbbbbbbb")

        mock.post(notify_url, text=load_fixture("pyarlo_success.json"))
        base_station = self.load_base_station(mock)

        base_station.mode = "Inside"
        request_number = mock.call_count - 2
        request = mock.request_history[request_number]
        self.assertEqual(
            "{}://{}{}".format(request.scheme, request.netloc, request.path),
            notify_url
        )

        body = request.json()
        self.assertEqual(body.get("publishResponse"), "true")
        self.assertEqual(body.get("action"), "set")
        self.assertEqual(body.get("resource"), "modes")
        self.assertEqual(body.get("properties"), {"active": "mode3"})
