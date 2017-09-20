"""The tests for the PyArlo platform."""
import unittest
from mock import patch
from pyarlo import ArloBaseStation, PyArlo
from tests.common import load_fixture

import json
import requests_mock

from pyarlo.const import (
    DEVICES_ENDPOINT, LIBRARY_ENDPOINT, LOGIN_ENDPOINT)

USERNAME = "foo"
PASSWORD = "bar"
USERID = "999-123456"


class TestArloBaseStationModes(unittest.TestCase):
    """Tests for ArloBaseStation component modes."""

    def load_modes(self, _):
        return json.loads(load_fixture("pyarlo_modes.json"))

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_modes)
    def test_current_mode(self, mock):
        """Test PyArlo BaseStation.mode property."""
        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture("pyarlo_authentication.json"))
        mock.get(DEVICES_ENDPOINT, text=load_fixture("pyarlo_devices.json"))
        mock.post(LIBRARY_ENDPOINT, text=load_fixture("pyarlo_videos.json"))

        arlo = PyArlo(USERNAME, PASSWORD, days=1)
        base_station = arlo.base_stations[0]
        print base_station.mode

        self.assertEqual(base_station.mode, "disarmed")
