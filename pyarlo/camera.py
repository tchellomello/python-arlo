# coding: utf-8
"""Generic Python Class file for Netgear Arlo camera module."""
import logging
from pyarlo.const import (
    RESET_CAM_ENDPOINT, STREAM_ENDPOINT, STREAMING_BODY)
from pyarlo.media import ArloMediaLibrary
from pyarlo.utils import http_get

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
    def user_id(self):
        """Return userID."""
        return self._attrs.get('userId')

    @property
    def unseen_videos(self):
        """Return number of unseen videos."""
        self.update()
        return self._attrs.get('mediaObjectCount')

    @property
    def unseen_videos_reset(self):
        """Reset the unseen videos counter."""
        url = RESET_CAM_ENDPOINT.format(self.unique_id)
        ret = self._session.query(url).get('success')
        self.update()
        return ret

    @property
    def user_role(self):
        """Return userRole."""
        return self._attrs.get('userRole')

    @property
    def last_image(self):
        """Return last image capture by camera."""
        self.update()
        return http_get(self._attrs.get('presignedLastImageUrl'))

    @property
    def last_video(self):
        """Return the last <ArloVideo> object from camera."""
        library = ArloMediaLibrary(self._session, preload=False)
        try:
            return library.load(only_cameras=[self], limit=1)[0]
        except IndexError:
            return None

    def videos(self, days=180):
        """
        Return all <ArloVideo> objects from camera given days range

        :param days: number of days to retrieve
        """
        library = ArloMediaLibrary(self._session, preload=False)
        try:
            return library.load(only_cameras=[self], days=days)
        except (AttributeError, IndexError):
            return []

    @property
    def captured_today(self):
        """Return list of <ArloVideo> object captured today."""
        return self.videos(days=0)

    @property
    def play_last_video(self):
        """Play last <ArloVideo> recorded from camera."""
        video = self.last_video
        return video.download_video()

    @property
    def xcloud_id(self):
        """Return X-Cloud-ID attribute."""
        return self._attrs.get('xCloudId')

    @property
    def get_battery_level(self):
        """Get the camera battery level."""
        base = self._session.base_stations[0]
        return base.get_camera_battery_level[self.device_id]

    @property
    def get_signal_strength(self):
        """Get the camera Signal strength."""
        base = self._session.base_stations[0]
        props = base.get_camera_properties
        if not props:
            return None
        for cam in props:
            if cam['serialNumber'] == self.device_id:
                return cam['signalStrength']

        return None

    @property
    def get_brightness(self):
        """Get the brightness property of camera."""
        base = self._session.base_stations[0]
        props = base.get_camera_properties
        if not props:
            return None
        for cam in props:
            if cam['serialNumber'] == self.device_id:
                return cam['brightness']

        return None

    @property
    def get_mirror_state(self):
        """Get the brightness property of camera."""
        base = self._session.base_stations[0]
        props = base.get_camera_properties
        if not props:
            return None
        for cam in props:
            if cam['serialNumber'] == self.device_id:
                return cam['flip']

        return None

    @property
    def get_flip_state(self):
        """Get the brightness property of camera."""
        base = self._session.base_stations[0]
        props = base.get_camera_properties
        if not props:
            return None
        for cam in props:
            if cam['serialNumber'] == self.device_id:
                return cam['mirror']

        return None

    @property
    def get_powersave_mode(self):
        """Get the brightness property of camera."""
        base = self._session.base_stations[0]
        props = base.get_camera_properties
        if not props:
            return None
        for cam in props:
            if cam['serialNumber'] == self.device_id:
                return cam['powerSaveMode']

        return None

    @property
    def is_camera_connected(self):
        """Connectivity status of Cam with Base Station."""
        base = self._session.base_stations[0]
        props = base.get_camera_properties
        if not props:
            return None
        for cam in props:
            if cam['serialNumber'] == self.device_id:
                return bool(cam['connectionState'] == 'available')

        return None

    @property
    def get_motion_detection_sensitivity(self):
        """Sensitivity level of Camera motion detection."""
        base = self._session.base_stations[0]
        props = base.get_camera_properties
        if not props:
            return None
        for cam in props:
            if cam['serialNumber'] == self.device_id:
                this_cam = cam
        triggers = this_cam['capabilities'][9]['Triggers']
        return triggers[0]['sensitivity']['default']

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
