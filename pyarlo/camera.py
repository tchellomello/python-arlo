# coding: utf-8
"""Generic Python Class file for Netgear Arlo camera module."""
import logging
from pyarlo.const import (
    RESET_CAM_ENDPOINT, STREAM_ENDPOINT, STREAMING_BODY,
    SNAPSHOTS_ENDPOINT, SNAPSHOTS_BODY, PRELOAD_DAYS)
from pyarlo.media import ArloMediaLibrary
from pyarlo.utils import http_get
from pyarlo.utils import assert_is_dict

_LOGGER = logging.getLogger(__name__)


class ArloCamera(object):
    """Arlo Camera module implementation."""

    def __init__(self, name, attrs, arlo_session,
                 min_days_vdo_cache=PRELOAD_DAYS):
        """Initialize Arlo camera object.

        :param name: Camera name
        :param attrs: Camera attributes
        :param arlo_session: PyArlo shared session
        :param min_days_vdo_cache: min. days to preload in video cache
        """
        self.name = name
        self._attrs = attrs
        self._session = arlo_session
        self._cached_videos = None
        self._min_days_vdo_cache = min_days_vdo_cache

        # make sure self._attrs is a dict
        self._attrs = assert_is_dict(self._attrs)

    def __repr__(self):
        """Representation string of object."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    @property
    def attrs(self):
        """Return device attributes."""
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        """Override device attributes."""
        self._attrs = value

    @property
    def min_days_vdo_cache(self):
        """Return minimal days to lookup when building the video cache."""
        return self._min_days_vdo_cache

    @min_days_vdo_cache.setter
    def min_days_vdo_cache(self, value):
        """Set minimal days to lookup when building the video cache."""
        self._min_days_vdo_cache = value

    # pylint: disable=invalid-name
    @property
    def device_id(self):
        """Return device_id."""
        if self._attrs is not None:
            return self._attrs.get('deviceId')
        return None

    @property
    def serial_number(self):
        """Return serial_number."""
        return self.device_id

    @property
    def device_type(self):
        """Return device_type."""
        if self._attrs is not None:
            return self._attrs.get('deviceType')
        return None

    @property
    def model_id(self):
        """Return model_id."""
        if self._attrs is not None:
            return self._attrs.get('modelId')
        return None

    @property
    def hw_version(self):
        """Return hardware version."""
        if self._attrs is not None:
            return self._attrs.get('properties').get('hwVersion')
        return None

    @property
    def parent_id(self):
        """Return camera parentID."""
        if self._attrs is not None:
            return self._attrs.get('parentId')
        return None

    @property
    def timezone(self):
        """Return timezone."""
        if self._attrs is not None:
            return self._attrs.get('properties').get('olsonTimeZone')
        return None

    @property
    def unique_id(self):
        """Return unique_id."""
        if self._attrs is not None:
            return self._attrs.get('uniqueId')
        return None

    @property
    def user_id(self):
        """Return userID."""
        if self._attrs is not None:
            return self._attrs.get('userId')
        return None

    @property
    def unseen_videos(self):
        """Return number of unseen videos."""
        if self._attrs is not None:
            return self._attrs.get('mediaObjectCount')
        return None

    def unseen_videos_reset(self):
        """Reset the unseen videos counter."""
        url = RESET_CAM_ENDPOINT.format(self.unique_id)
        ret = self._session.query(url).get('success')
        return ret

    @property
    def user_role(self):
        """Return userRole."""
        if self._attrs is not None:
            return self._attrs.get('userRole')
        return None

    @property
    def last_image(self):
        """Return last image captured by camera."""
        if self._attrs is not None:
            return http_get(self._attrs.get('presignedLastImageUrl'))
        return None

    @property
    def last_image_from_cache(self):
        """
        Return last thumbnail present in self._cached_images.

        This is useful in Home Assistant when the ArloHub has not
        updated all information, but the camera.arlo already pulled
        the last image. Using this method, everything is kept synced.
        """
        if self.last_video:
            return http_get(self.last_video.thumbnail_url)
        return None

    @property
    def last_video(self):
        """Return the last <ArloVideo> object from camera."""
        if self._cached_videos is None:
            self.make_video_cache()

        if self._cached_videos:
            return self._cached_videos[0]
        return None

    def make_video_cache(self, days=None):
        """Save videos on _cache_videos to avoid dups."""
        if days is None:
            days = self._min_days_vdo_cache
        self._cached_videos = self.videos(days)

    def videos(self, days=None):
        """
        Return all <ArloVideo> objects from camera given days range

        :param days: number of days to retrieve
        """
        if days is None:
            days = self._min_days_vdo_cache
        library = ArloMediaLibrary(self._session, preload=False)
        try:
            return library.load(only_cameras=[self], days=days)
        except (AttributeError, IndexError):
            # make sure we are returning an empty list istead of None
            # returning an empty list, cache will be forced only when calling
            # the update method. Changing this can impact badly
            # in the Home Assistant performance
            return []

    @property
    def captured_today(self):
        """Return list of <ArloVideo> object captured today."""
        if self._cached_videos is None:
            self.make_video_cache()

        return [vdo for vdo in self._cached_videos if vdo.created_today]

    def play_last_video(self):
        """Play last <ArloVideo> recorded from camera."""
        video = self.last_video
        return video.download_video()

    @property
    def xcloud_id(self):
        """Return X-Cloud-ID attribute."""
        if self._attrs is not None:
            return self._attrs.get('xCloudId')
        return None

    @property
    def base_station(self):
        """Return the base_station assigned for the given camera."""
        try:
            return list(filter(lambda x: x.device_id == self.parent_id,
                               self._session.base_stations))[0]
        except (IndexError, AttributeError):
            return None

    def _get_camera_properties(self):
        """Lookup camera properties from base station."""
        if self.base_station and self.base_station.camera_properties:
            for cam in self.base_station.camera_properties:
                if cam["serialNumber"] == self.device_id:
                    return cam
        return None

    @property
    def properties(self):
        """Get this camera's properties."""
        return self._get_camera_properties()

    @property
    def capabilities(self):
        """Get a camera's capabilities."""
        properties = self.properties
        return properties.get("capabilities") if properties else None

    @property
    def triggers(self):
        """Get a camera's triggers."""
        capabilities = self.capabilities
        if not capabilities:
            return None

        for capability in capabilities:
            if not isinstance(capability, dict):
                continue

            triggers = capability.get("Triggers")
            if triggers:
                return triggers

        return None

    @property
    def battery_level(self):
        """Get the camera battery level."""
        properties = self.properties
        return properties.get("batteryLevel") if properties else None

    @property
    def signal_strength(self):
        """Get the camera Signal strength."""
        properties = self.properties
        return properties.get("signalStrength") if properties else None

    @property
    def brightness(self):
        """Get the brightness property of camera."""
        properties = self.properties
        return properties.get("brightness") if properties else None

    @property
    def mirror_state(self):
        """Get the mirror state of camera image."""
        properties = self.properties
        return properties.get("mirror") if properties else None

    @property
    def flip_state(self):
        """Get the flipped state of camera image."""
        properties = self.properties
        return properties.get("flip") if properties else None

    @property
    def powersave_mode(self):
        """Get the power mode (stream quality) of camera."""
        properties = self.properties
        return properties.get("powerSaveMode") if properties else None

    @property
    def is_camera_connected(self):
        """Connectivity status of Cam with Base Station."""
        properties = self.properties
        return bool(properties.get("connectionState") == "available") \
            if properties else None

    @property
    def motion_detection_sensitivity(self):
        """Sensitivity level of Camera motion detection."""
        if not self.triggers:
            return None

        for trigger in self.triggers:
            if trigger.get("type") != "pirMotionActive":
                continue

            sensitivity = trigger.get("sensitivity")
            if sensitivity:
                return sensitivity.get("default")

        return None

    @property
    def audio_detection_sensitivity(self):
        """Sensitivity level of Camera audio detection."""
        if not self.triggers:
            return None

        for trigger in self.triggers:
            if trigger.get("type") != "audioAmplitude":
                continue

            sensitivity = trigger.get("sensitivity")
            if sensitivity:
                return sensitivity.get("default")

        return None

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

    @property
    def snapshot_url(self):
        """Return the snapshot url."""
        # Snapshot should be scheduled first.  It will
        # available a couple seconds after.
        # If a GET request fails on this URL, trying
        # again is logical since the snapshot isn't
        # taken immediately.  Snapshots will be cached for a
        # predefined amount of time.
        return self._attrs.get('presignedFullFrameSnapshotUrl')

    def schedule_snapshot(self):
        """Trigger snapshot to be uploaded to AWS.
        Return success state."""
        # Notes:
        #  - Snapshots are not immediate.
        #  - Snapshots will be cached for predefined amount
        #    of time.
        #  - Snapshots are not balanced. To get a better
        #    image, it must be taken from the stream, a few
        #    seconds after stream start.
        url = SNAPSHOTS_ENDPOINT
        params = SNAPSHOTS_BODY
        params['from'] = "{0}_web".format(self.user_id)
        params['to'] = self.device_id
        params['resource'] = "cameras/{0}".format(self.device_id)
        params['transId'] = "web!{0}".format(self.xcloud_id)

        # override headers
        headers = {'xCloudId': self.xcloud_id}

        _LOGGER.debug("Snapshot device %s", self.name)
        _LOGGER.debug("Device params %s", params)
        _LOGGER.debug("Device headers %s", headers)

        ret = self._session.query(url,
                                  method='POST',
                                  extra_params=params,
                                  extra_headers=headers)

        _LOGGER.debug("Snapshot results %s", ret)

        return ret is not None and ret.get('success')

    def update(self):
        """Update object properties."""
        self._attrs = self._session.refresh_attributes(self.name)
        self._attrs = assert_is_dict(self._attrs)

        # force base_state to update properties
        if self.base_station:
            self.base_station.update()

# vim:sw=4:ts=4:et:
