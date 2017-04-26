# coding: utf-8
"""Implementation of Arlo utils."""
import requests


def http_get(url, filename=None):
    """Download HTTP data."""
    ret = requests.get(url)
    if ret.status_code != 200:
        return False

    if filename is None:
        return ret.content
    else:
        with open(filename, 'wb') as data:
            data.write(ret.content)
    return True

# vim:sw=4:ts=4:et:
