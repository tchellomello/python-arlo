# coding: utf-8
"""Base Python Class file for Netgear Arlo camera module."""
import logging
import requests

from pyarlo.base_station import ArloBaseStation
from pyarlo.camera import ArloCamera
from pyarlo.media import ArloMediaLibrary
from pyarlo.const import (
    BILLING_ENDPOINT, DEVICES_ENDPOINT,
    FRIENDS_ENDPOINT, LOGIN_ENDPOINT, PROFILE_ENDPOINT,
    PRELOAD_DAYS, RESET_ENDPOINT)

_LOGGER = logging.getLogger(__name__)


class PyArlo(object):
    """Base object for Netgar Arlo camera."""

    def __init__(self, username=None, password=None,
                 preload=True, days=PRELOAD_DAYS):
        """Create a PyArlo object.

        :param username: Arlo user email
        :param password: Arlo user password
        :param preload: Boolean to preload video library.
        :param days: If preload, number of days to lookup.

        :returns PyArlo base object
        """
        self.authenticated = None
        self.country_code = None
        self.date_created = None
        self.userid = None
        self.__token = None
        self.__headers = None
        self.__params = None

        self._all_devices = {}

        # set username and password
        self.__password = password
        self.__username = username
        self.session = requests.Session()

        # login user
        self.login()

        # pylint: disable=invalid-name
        self.ArloMediaLibrary = ArloMediaLibrary(self,
                                                 preload=preload,
                                                 days=days)

    def __repr__(self):
        """Object representation."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.userid)

    def login(self):
        """Login to the Arlo account."""
        _LOGGER.debug("Creating Arlo session")
        self._authenticate()

    def _authenticate(self):
        """Authenticate user and generate token."""
        self.cleanup_headers()
        url = LOGIN_ENDPOINT
        data = self.query(
            url,
            method='POST',
            extra_params={
                'email': self.__username,
                'password': self.__password
            })

        if isinstance(data, dict) and data.get('success'):
            data = data.get('data')
            self.authenticated = data.get('authenticated')
            self.country_code = data.get('countryCode')
            self.date_created = data.get('dateCreated')
            self.__token = data.get('token')
            self.userid = data.get('userId')

            # update header with the generated token
            self.__headers['Authorization'] = self.__token

    def cleanup_headers(self):
        """Reset the headers and params."""
        headers = {'Content-Type': 'application/json'}
        headers['Authorization'] = self.__token
        self.__headers = headers
        self.__params = {}

    def query(self,
              url,
              method='GET',
              extra_params=None,
              extra_headers=None,
              retry=3,
              raw=False,
              stream=False):
        """
        Return a JSON object or raw session.

        :param url:  Arlo API URL
        :param method: Specify the method GET, POST or PUT. Default is GET.
        :param extra_params: Dictionary to be appended on request.body
        :param extra_headers: Dictionary to be apppended on request.headers
        :param retry: Attempts to retry a query. Default is 3.
        :param raw: Boolean if query() will return request object instead JSON.
        :param stream: Boolean if query() will return a stream object.
        """
        response = None
        loop = 0

        # always make sure the headers and params are clean
        self.cleanup_headers()

        while loop <= retry:

            # override request.body or request.headers dictionary
            if extra_params:
                params = self.__params
                params.update(extra_params)
            else:
                params = self.__params
            _LOGGER.debug("Params: %s", params)

            if extra_headers:
                headers = self.__headers
                headers.update(extra_headers)
            else:
                headers = self.__headers
            _LOGGER.debug("Headers: %s", headers)

            _LOGGER.debug("Querying %s on attempt: %s/%s", url, loop, retry)
            loop += 1

            # define connection method
            req = None

            if method == 'GET':
                req = self.session.get(url, headers=headers, stream=stream)
            elif method == 'PUT':
                req = self.session.put(url, json=params, headers=headers)
            elif method == 'POST':
                req = self.session.post(url, json=params, headers=headers)

            if req and (req.status_code == 200):
                if raw:
                    _LOGGER.debug("Required raw object.")
                    response = req
                else:
                    response = req.json()

                # leave if everything worked fine
                break

        return response

    @property
    def cameras(self):
        """Return all cameras linked on Arlo account."""
        return self.devices.get('cameras')

    @property
    def base_stations(self):
        """Return all base stations linked on Arlo account."""
        return self.devices.get('base_station')

    @property
    def devices(self):
        """Return all devices on Arlo account."""
        if self._all_devices:
            return self._all_devices

        self._all_devices = {}
        self._all_devices['cameras'] = []
        self._all_devices['base_station'] = []

        url = DEVICES_ENDPOINT
        data = self.query(url)

        for device in data.get('data'):
            name = device.get('deviceName')
            if ((device.get('deviceType') == 'camera' or
                 device.get('deviceType') == 'arloq' or
                 device.get('deviceType') == 'arloqs') and
                    device.get('state') == 'provisioned'):
                camera = ArloCamera(name, device, self)
                self._all_devices['cameras'].append(camera)

            if (device.get('state') == 'provisioned' and
                    (device.get('deviceType') == 'basestation' or
                     device.get('modelId') == 'ABC1000')):
                base = ArloBaseStation(name, device, self.__token, self)
                self._all_devices['base_station'].append(base)

        return self._all_devices

    def lookup_camera_by_id(self, device_id):
        """Return camera object by device_id."""
        camera = list(filter(
            lambda cam: cam.device_id == device_id, self.cameras))[0]
        if camera:
            return camera
        return None

    def refresh_attributes(self, name):
        """Refresh attributes from a given Arlo object."""
        url = DEVICES_ENDPOINT
        response = self.query(url)

        if not response or not isinstance(response, dict):
            return None

        for device in response.get('data'):
            if device.get('deviceName') == name:
                return device
        return None

    @property
    def unseen_videos_reset(self):
        """Reset the unseen videos counter for all cameras."""
        return self.query(RESET_ENDPOINT).get('success')

    @property
    def billing_information(self):
        """Return billing json."""
        url = BILLING_ENDPOINT
        return self.query(url)

    @property
    def shared_users(self):
        """Return shared users json."""
        url = FRIENDS_ENDPOINT
        return self.query(url)

    @property
    def profile(self):
        """Return user profile json."""
        url = PROFILE_ENDPOINT
        return self.query(url)

    @property
    def is_connected(self):
        """Connection status of client with Arlo system."""
        return bool(self.authenticated)

    def update(self, update_cameras=False, update_base_station=False):
        """Refresh object."""
        self._authenticate()

        # update attributes in all cameras to avoid duped queries
        if update_cameras:
            url = DEVICES_ENDPOINT
            response = self.query(url)
            if not response or not isinstance(response, dict):
                return

            for camera in self.cameras:
                for dev_info in response.get('data'):
                    if dev_info.get('deviceName') == camera.name:
                        _LOGGER.debug("Refreshing %s attributes", camera.name)
                        camera.attrs = dev_info

                # preload cached videos
                # the user is still able to force a new query by
                # calling the Arlo.video()
                camera.make_video_cache()

        # force update base_station
        if update_base_station:
            for base in self.base_stations:
                base.update()

# vim:sw=4:ts=4:et:
