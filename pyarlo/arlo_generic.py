# coding: utf-8
# vim:sw=4:ts=4:et:
"""Generic Python Class file for Netgear Arlo camera module."""


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
    def id(self):
        """Return object id."""
        return self._attrs.get('deviceId')

    @property
    def model_id(self):
        """Return model_id."""
        return self._attrs.get('modelId')
