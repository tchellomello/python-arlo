"""Helper methods for tests."""
import json
import os


def open_fixture(filename, binary=False):
    """Open a fixture file."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    mode = "rb" if binary else "r"
    return open(path, mode)


def load_fixture(filename, binary=False):
    """Load a fixture."""
    fixture = open_fixture(filename, binary)
    with fixture as fdp:
        return fdp.read()


def load_fixture_json(filename):
    """Load a fixture JSON into a dict."""
    fixture = load_fixture(filename)
    return json.loads(fixture)


def load_base_properties(*args, **kwargs):
    """Load base station properties into a dict."""
    return load_fixture_json("pyarlo_base_station_properties.json")


def load_camera_properties(*args, **kwargs):
    """Load camera properties into a dict."""
    return load_fixture_json("pyarlo_camera_properties.json")


def load_camera_rules(*args, **kwargs):
    """Load camera rules into a dict."""
    return load_fixture_json("pyarlo_camera_rules.json")


def load_camera_schedule(*args, **kwargs):
    """Load camera schedule into a dict."""
    schedule = load_fixture_json("pyarlo_camera_schedule.json")
    if kwargs.get("active", False):
        schedule["properties"]["active"] = kwargs["active"]
    return schedule


def load_camera_live_streaming(*args, **kwargs):
    """Load camera live streaming response as dict."""
    return load_fixture_json("pyarlo_camera_live_streaming.json")


def load_camera_schedule_snapshot(*args, **kwargs):
    """Load camera live streaming response as dict."""
    return load_fixture_json("pyarlo_success.json")


def load_ambient_sensor_data(*args, **kwargs):
    """Load ambient sensor data."""
    return load_fixture_json("pyarlo_ambient_sensors.json")


def load_audio_playback_status(*args, **kwargs):
    """Load audio playback status."""
    return load_fixture_json("pyarlo_audio_playback.json")


def load_extended_properties(*args, **kwargs):
    """Load extended camera properties."""
    return load_fixture_json("pyarlo_extended_properties.json")
