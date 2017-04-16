# coding: utf-8
# vim:sw=4:ts=4:et:
"""Generic Python Class file for Netgear Arlo camera module."""
from pyarlo.const import ACTION_MODES, ACTION_STRUCT, API_URL, NOTIFY_ENDPOINT


class ArloGeneric(object):
    """Generic Implementation for Arlo object."""

    def __init__(self, name, attrs, arlo):
        """Initialize Arlo generic object."""
        self.name = name
        self._attrs = attrs
        self._arlo = arlo

    def __repr__(self):
        """Representation string of object."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    # pylint: disable=invalid-name
    @property
    def device_id(self):
        """Return object id."""
        return self._attrs.get('deviceId')

    @property
    def model_id(self):
        """Return model_id."""
        return self._attrs.get('modelId')

    @property
    def hw_version(self):
        """Return hardware version."""
        return self._attrs.get('properties').get('hwVersion')

    @property
    def timezone(self):
        """Return timezone."""
        return self._attrs.get('properties').get('olsonTimeZone')

    @property
    def unique_id(self):
        """Return unique_id."""
        return self._attrs.get('uniqueId')

    @property
    def serial_number(self):
        """Return serial number."""
        return self._attrs.get('properties').get('serialNumber')

    @property
    def user_id(self):
        """Return userID."""
        return self._attrs.get('userId')

    @property
    def xcloud_id(self):
        """Return X-Cloud-ID attribute."""
        return self._attrs('xCloudId')

    def get_last_update(self):
        """Return when camera got updated."""
        return self._attrs('lastModified')

    def _run_action(self, action):
        """Run action."""
        url = API_URL + NOTIFY_ENDPOINT.format(self.device_id)
        json = ACTION_STRUCT
        json['from'] = "{0}_web".format(self.user_id)
        json['to'] = self.device_id
        json['properties'] = {'active': ACTION_MODES.get(action)}
        self._arlo.query(url, method='POST',
                         extra_headers={"xCloudId": self.xcloud_id})

    @property
    def arm(self):
        """Arm camera."""
        return print(self._run_action('arm'))

    @property
    def disarm(self):
        """Disarm camera."""
        return print(self._run_action('disarm'))

    def update(self):
        """Update object properties."""
        return None
