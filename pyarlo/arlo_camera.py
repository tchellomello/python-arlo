# coding: utf-8
# vim:sw=4:ts=4:et:
"""Netgear Arlo camera module."""
from pyarlo.arlo_generic import ArloGeneric


class ArloCamera(ArloGeneric):
    """Arlo Camera module implementation."""

    @property
    def snapshot_url(self):
        """Return snapshot url."""
        return self._attrs.get('presignedLastImageUrl')

    def download_snapshot(self, filename=None):
        """Download JPEG snapshot."""
        if filename is None:
            ret = self._arlo.session.get(self.snapshot_url)
            if ret.status_code == 200:
                return ret.content
        return False
