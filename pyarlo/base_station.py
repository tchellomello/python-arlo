# coding: utf-8
"""Generic Python Class file for Netgear Arlo Base Station module."""
import logging

_LOGGER = logging.getLogger(__name__)


class ArloBaseStation(object):
    """Arlo Base Station module implementation."""

    def __init__(self, name, attrs, arlo_session):
        """Initialize Arlo Base Station object.

        :param name: Base Station name
        :param attrs: Attributes
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
    def device_type(self):
        """Return device_type."""
        return self._attrs.get('deviceType')

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

    def update(self):
        """Update object properties."""
        self._attrs = self._session.refresh_attributes(self.name)

# vim:sw=4:ts=4:et:
