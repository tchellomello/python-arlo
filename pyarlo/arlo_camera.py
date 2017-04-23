# coding: utf-8
# vim:sw=4:ts=4:et:
"""Netgear Arlo camera module."""
from pyarlo.arlo_generic import ArloGeneric


class ArloCamera(ArloGeneric):
    """Arlo Camera module implementation."""

    def __init__(self, name, attrs, arlo):
        """Initialize Arlo generic object."""
        super(ArloCamera, self).__init__(name, attrs, arlo)
        self._attrs = attrs
        self._arlo = arlo
        self.name = name

    @property
    def snapshot_url(self):
        """Return snapshot url."""
        return self._attrs.get('presignedLastImageUrl')

    def download_snapshot(self, filename=None):
        """Download JPEG snapshot."""
        ret = self._arlo.session.get(self.snapshot_url)

        if ret.status_code != 200:
            return False

        if filename is None:
            return ret.content
        else:
            with open(filename, 'wb') as snapshot:
                snapshot.write(ret.content)
        return True
