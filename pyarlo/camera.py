# coding: utf-8
"""Generic Python Class file for Netgear Arlo camera module."""
import logging
from pyarlo.const import (
    ACTION_MODES, NOTIFY_ENDPOINT, RUN_ACTION_BODY,
    STREAM_ENDPOINT, STREAMING_BODY)

_LOGGER = logging.getLogger(__name__)


class ArloCamera(object):
    """Arlo Camera module implementation."""

    def __init__(self, name, attrs, arlo_session):
        """Initialize Arlo camera object.

        :param name: Camera name
        :param attrs: Camera attributes
        :param arlo_session: PyArlo shared session
        """
        self.name = name
        self._attrs = attrs
        self._session = arlo_session

    def __repr__(self):
        """Representation string of object."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    # pylint: disable=invalid-name
    @property
    def device_id(self):
        """Return device_id."""
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

    def __run_action(self, action):
        """Run action."""
        url = NOTIFY_ENDPOINT.format(self.device_id)
        body = RUN_ACTION_BODY
        body['from'] = "{0}_web".format(self.user_id)
        body['to'] = self.device_id
        body['properties'] = {'active': ACTION_MODES.get(action)}

        _LOGGER.debug("Action body: %s", body)

        ret = \
            self._session.query(url, method='POST', extra_params=body,
                                extra_headers={"xCloudId": self.xcloud_id})
        return ret.get('success')

    @property
    def available_modes(self):
        """Return list of available modes."""
        return ACTION_MODES.keys()

    @property
    def mode(self):
        """Return current mode."""
        return None

    @mode.setter
    def mode(self, mode):
        """Set Arlo camera mode.

        :param mode: arm, disarm
        """
        if mode not in ACTION_MODES.keys():
            return "Invalid mode"
        return self.__run_action(mode)

    def live_streaming(self):
        """Return live streaming generator."""
        url = STREAM_ENDPOINT

        # override params
        params = STREAMING_BODY
        params['from'] = "{0}_web".format(self.user_id)
        params['to'] = self.device_id
        params['resource'] = "cameras/{0}".format(self.device_id)
        params['transId'] = "web!{0}".format(self.xcloud_id)

        # override headers
        headers = {'xCloudId': self.xcloud_id}

        _LOGGER.debug("Streaming device %s", self.name)
        _LOGGER.debug("Device params %s", params)
        _LOGGER.debug("Device headers %s", headers)

        ret = self._session.query(url,
                                  method='POST',
                                  extra_params=params,
                                  extra_headers=headers)

        _LOGGER.debug("Streaming results %s", ret)
        if ret.get('success'):
            return ret.get('data').get('url')
        return ret.get('data')

    def update(self):
        """Update object properties."""
        self._attrs = self._session.refresh_attributes(self.name)

# vim:sw=4:ts=4:et:
