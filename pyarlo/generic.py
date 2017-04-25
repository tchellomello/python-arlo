# coding: utf-8
"""Generic Python Class file for Netgear Arlo camera module."""
from pyarlo.const import ACTION_MODES, NOTIFY_ENDPOINT, RUN_ACTION_BODY


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
    def user_role(self):
        """Return userRole."""
        return self._attrs.get('userRole')

    @property
    def xcloud_id(self):
        """Return X-Cloud-ID attribute."""
        return self._attrs.get('xCloudId')

    @property
    def updated_at(self):
        """Return when camera got updated."""
        return self._attrs.get('lastModified')

    def _run_action(self, action):
        """Run action."""
        url = NOTIFY_ENDPOINT.format(self.device_id)
        body = RUN_ACTION_BODY
        body['from'] = "{0}_web".format(self.user_id)
        body['to'] = self.device_id
        body['properties'] = {'active': ACTION_MODES.get(action)}

        ret = \
            self._arlo.query(url, method='POST', extra_params=body,
                             extra_headers={"xCloudId": self.xcloud_id})
        return ret.get('success')

    def set_mode(self, mode):
        """Set Arlo camera mode.

        :param mode: arm, disarm
        """
        if mode in ACTION_MODES.keys():
            return self._run_action(mode)

    def update(self):
        """Update object properties."""
        self._attrs = self._arlo._refresh_attributes(self.name)

# vim:sw=4:ts=4:et:
