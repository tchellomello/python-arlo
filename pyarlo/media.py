# coding: utf-8
"""Implementation of Arlo Media object."""
import logging
from datetime import datetime
from datetime import timedelta
from pyarlo.const import LIBRARY_ENDPOINT, PRELOAD_DAYS
from pyarlo.utils import (
    http_get, http_stream, to_datetime, pretty_timestamp,
    assert_is_dict)

_LOGGER = logging.getLogger(__name__)


class ArloMediaLibrary(object):
    """Arlo Library Media module implementation."""

    def __init__(self, arlo_session, preload=True, days=PRELOAD_DAYS):
        """Initialiaze Arlo Media Library object.

        :param arlo_session: PyArlo shared session
        :param preload: Boolean to pre-load video library.
        :param days: If preload, number of days to lookup.

        :returns ArloMediaLibrary object
        """
        self._session = arlo_session

        if preload and days:
            self.videos = self.load(days)
        else:
            self.videos = []

    def __repr__(self):
        """Representation string of object."""
        return "<{0}: {1}>".format(self.__class__.__name__,
                                   self._session.userid)

    def load(self, days=PRELOAD_DAYS, only_cameras=None,
             date_from=None, date_to=None, limit=None):
        """Load  Arlo videos from the given criteria

        :param days: number of days to retrieve
        :param only_cameras: retrieve only <ArloCamera> on that list
        :param date_from: refine from initial date
        :param date_to: refine final date
        :param limit: define number of objects to return
        """
        videos = []
        url = LIBRARY_ENDPOINT
        if not (date_from and date_to):
            now = datetime.today()
            date_from = (now - timedelta(days=days)).strftime('%Y%m%d')
            date_to = now.strftime('%Y%m%d')

        params = {'dateFrom': date_from, 'dateTo': date_to}
        data = self._session.query(url,
                                   method='POST',
                                   extra_params=params).get('data')

        # get all cameras to append to create ArloVideo object
        all_cameras = self._session.cameras

        for video in data:
            # pylint: disable=cell-var-from-loop
            srccam = \
                list(filter(
                    lambda cam: cam.device_id == video.get('deviceId'),
                    all_cameras)
                    )[0]

            # make sure only_cameras is a list
            if only_cameras and \
               not isinstance(only_cameras, list):
                only_cameras = [(only_cameras)]

            # filter by camera only
            if only_cameras:
                if list(filter(lambda cam: cam.device_id == srccam.device_id,
                               list(only_cameras))):
                    videos.append(ArloVideo(video, srccam, self._session))
            else:
                videos.append(ArloVideo(video, srccam, self._session))

        if limit:
            return videos[:limit]

        return videos


class ArloVideo(object):
    """Object for Arlo Video file."""

    def __init__(self, attrs, camera, arlo_session):
        """Initialiaze Arlo Video object.

        :param attrs: Video attributes
        :param camera: Arlo camera which recorded the video
        :param arlo_session: Arlo shared session
        """
        self._attrs = attrs
        self._attrs = assert_is_dict(self._attrs)
        self._camera = camera
        self._session = arlo_session

    def __repr__(self):
        """Representation string of object."""
        return "<{0}: {1}>".format(self.__class__.__name__, self._name)

    @property
    def _name(self):
        """Define object name."""
        return "{0} {1} {2}".format(
            self._camera.name,
            pretty_timestamp(self.created_at),
            self._attrs.get('mediaDuration'))

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Return object id."""
        if self._attrs is not None:
            return self._attrs.get('name')
        return None

    @property
    def created_at(self):
        """Return timestamp."""
        if self._attrs is not None:
            return self._attrs.get('localCreatedDate')
        return None

    def created_at_pretty(self, date_format=None):
        """Return pretty timestamp."""
        if date_format:
            return pretty_timestamp(self.created_at, date_format=date_format)
        return pretty_timestamp(self.created_at)

    @property
    def created_today(self):
        """Return True if created today."""
        if self.datetime.date() == datetime.today().date():
            return True
        return False

    @property
    def datetime(self):
        """Return datetime when video was created."""
        return to_datetime(self.created_at)

    @property
    def content_type(self):
        """Return content_type."""
        if self._attrs is not None:
            return self._attrs.get('contentType')
        return None

    @property
    def camera(self):
        """Return camera object that recorded video."""
        return self._camera

    @property
    def media_duration_seconds(self):
        """Return media duration in seconds."""
        if self._attrs is not None:
            return self._attrs.get('mediaDurationSecond')
        return None

    @property
    def triggered_by(self):
        """Return the reason why video was recorded."""
        if self._attrs is not None:
            return self._attrs.get('reason')
        return None

    @property
    def thumbnail_url(self):
        """Return thumbnail url."""
        if self._attrs is not None:
            return self._attrs.get('presignedThumbnailUrl')
        return None

    @property
    def video_url(self):
        """Return video content url."""
        if self._attrs is not None:
            return self._attrs.get('presignedContentUrl')
        return None

    def download_thumbnail(self, filename=None):
        """Download JPEG thumbnail.

        :param filename: File to save thumbnail. Default: stdout
        """
        return http_get(self.thumbnail_url, filename)

    def download_video(self, filename=None):
        """Download video content.

        :param filename: File to save video. Default: stdout
        """
        return http_get(self.video_url, filename)

    @property
    def stream_video(self):
        """Stream video."""
        return http_stream(self.video_url)

# vim:sw=4:ts=4:et:
