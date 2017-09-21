"""Helper methods for tests."""
import json
import os


def open_fixture(filename):
    """Open a fixture file."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    return open(path)


def load_fixture(filename):
    """Load a fixture."""
    fixture = open_fixture(filename)
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
    return load_fixture_json("pyarlo_camera_schedule.json")
