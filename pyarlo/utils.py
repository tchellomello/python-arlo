# coding: utf-8
"""Implementation of Arlo utils."""
import time
from datetime import datetime as dt
import requests


def to_datetime(timestamp):
    """Return datetime object from timestamp."""
    return dt.fromtimestamp(time.mktime(
        time.localtime(int(str(timestamp)[:10]))))


def pretty_timestamp(timestamp, date_format='%a-%m_%d_%y:%H:%M:%S'):
    """Huminize timestamp."""
    return time.strftime(date_format,
                         time.localtime(int(str(timestamp)[:10])))


def http_get(url, filename=None):
    """Download HTTP data."""
    ret = requests.get(url)
    if ret.status_code != 200:
        return False

    if filename is None:
        return ret.content

    with open(filename, 'wb') as data:
        data.write(ret.content)
    return True


def http_stream(url, chunk=4096):
    """Generate stream for a given record video.

    :param chunk: chunk bytes to read per time
    :returns generator object
    """
    ret = requests.get(url, stream=True)
    ret.raise_for_status()
    for data in ret.iter_content(chunk):
        yield data


def assert_is_dict(var):
    """Assert variable is from the type dictionary."""
    if var is None or not isinstance(var, dict):
        return {}
    return var

# vim:sw=4:ts=4:et:
