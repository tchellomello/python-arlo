# coding: utf-8
"""Generic Python Class file for Netgear Arlo Base Station module."""
import json
import threading
import time
import logging
import sseclient
from pyarlo.const import (
    ACTION_BODY, SUBSCRIBE_ENDPOINT, UNSUBSCRIBE_ENDPOINT,
    ACTION_MODES, NOTIFY_ENDPOINT, RESOURCES)
_LOGGER = logging.getLogger(__name__)


class ArloBaseStation(object):
    """Arlo Base Station module implementation."""

    def __init__(self, name, attrs, session_token, arlo_session):
        """Initialize Arlo Base Station object.

        :param name: Base Station name
        :param attrs: Attributes
        :param session_token: Session token passed by camera class
        :param arlo_session: PyArlo shared session
        """
        self.name = name
        self._attrs = attrs
        self._session = arlo_session
        self._session_token = session_token
        self.__sseclient = None
        self.__subscribed = False
        self.__events = []

    def __repr__(self):
        """Representation string of object."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    def thread_function(self):
        """Thread function."""
        url = SUBSCRIBE_ENDPOINT + "?token=" + self._session_token
        data = self._session.query(url, method='GET', raw=True, stream=True)
        self.__sseclient = sseclient.SSEClient(data)
        if self.__sseclient:
            self.__subscribed = True
        for event in (self.__sseclient).events():
            if not self.__subscribed:
                break
            data = json.loads(event.data)
            if data.get('status') == "connected":
                _LOGGER.debug("Successfully subscribed this base station")
            elif data.get('action'):
                action = data.get('action')
                resource = data.get('resource')
                if action == "logout":
                    _LOGGER.debug("Logged out by some other entity")
                    self.__subscribed = False
                    break
                elif action == "is" and "subscriptions/" not in resource:
                    self.__events.append(data)

    def _get_event_stream(self):
        """Spawn a thread and monitor the Arlo Event Stream."""
        event_thread = threading.Thread(target=self.thread_function)
        event_thread.start()

    def _subscribe_myself(self):
        """Subscribe this base station for all events."""
        return self.__run_action(
            method='SET',
            resource='subscribe',
            mode=None,
            publish_response=False)

    def _unsubscribe_myself(self):
        """Unsubscribe this base station for all events."""
        url = UNSUBSCRIBE_ENDPOINT
        return self._session.query(url, method='GET', raw=True, stream=False)

    def _close_event_stream(self):
        """Stop the Event stream thread."""
        self.__subscribed = False

    def publish_and_get_event(self, resource):
        """Publish and get the event from base station."""
        self._get_event_stream()
        self._subscribe_myself()

        this_event = ''
        status = self.__run_action(
            method='GET',
            resource=resource,
            mode=None,
            publish_response=False)
        if status == 'success':
            for i in range(0, 5):
                _LOGGER.debug("Trying instance " + str(i))
                time.sleep(1)
                for event in self.__events:
                    if event['resource'] == resource:
                        this_event = event
                        self.__events.remove(event)
                        break
                if this_event:
                    break

        self._unsubscribe_myself()
        self._close_event_stream()

        if this_event:
            return this_event

        return None

    def __run_action(
            self,
            method='GET',
            resource=None,
            mode=None,
            publish_response=None):
        """Run action.

        :param method: Specify the method GET, POST or PUT. Default is GET.
        :param resource: Specify one of the resources to fetch from arlo.
        :param mode: Specify the mode to set, else None for GET operations
        :param publish_response: Set to True for SETs. Default False
        """
        url = NOTIFY_ENDPOINT.format(self.device_id)

        body = ACTION_BODY

        if resource:
            body['resource'] = resource

        if method == 'GET':
            body['action'] = "get"
            body['properties'] = None
        elif method == 'SET':
            body['action'] = "set"
            if resource == 'schedule':
                body['properties'] = {'active': 'true'}
            elif resource == 'subscribe':
                body['resource'] = "subscriptions/" + \
                        "{0}_web".format(self.user_id)
                dev = []
                dev.append(self.device_id)
                body['properties'] = {'devices': dev}
            elif resource == 'modes':
                body['properties'] = {'active': ACTION_MODES.get(mode)}
        else:
            _LOGGER.info("Invalid method requested")
            return None

        if not publish_response:
            body['publishResponse'] = 'false'
        else:
            body['publishResponse'] = 'true'

        body['from'] = "{0}_web".format(self.user_id)
        body['to'] = self.device_id
        body['transId'] = "web!e6d1b969.8aa4b!1498165992111"

        _LOGGER.info("Action body: %s", body)

        ret = \
            self._session.query(url, method='POST', extra_params=body,
                                extra_headers={"xCloudId": self.xcloud_id})
        if ret.get('success'):
            return 'success'

        return None

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

    @property
    def available_modes(self):
        """Return list of available modes."""
        return list(ACTION_MODES.keys())

    @property
    def available_resources(self):
        """Return list of available resources."""
        return list(RESOURCES.keys())

    @property
    def mode(self):
        """Return current mode."""
        resource = "modes"
        mode_event = self.publish_and_get_event(resource)
        if mode_event:
            active_mode = mode_event['properties']['active']
            modes = mode_event['properties']['modes']
            for mode in modes:
                if mode['id'] == active_mode:
                    return mode['type']

        return None

    @property
    def get_camera_properties(self):
        """Return camera properties."""
        resource = "cameras"
        resource_event = self.publish_and_get_event(resource)
        if resource_event:
            return resource_event['properties']

        return None

    @property
    def get_camera_battery_level(self):
        """Return a list of battery levels of all cameras."""
        battery_levels = {}
        resource = "cameras"
        resource_event = self.publish_and_get_event(resource)
        if resource_event:
            cameras = resource_event['properties']
            for camera in cameras:
                battery_levels[camera['serialNumber']] = camera['batteryLevel']
            return battery_levels

        return None

    @property
    def get_basestation_properties(self):
        """Return the base station info."""
        resource = "basestation"
        basestn_event = self.publish_and_get_event(resource)
        if basestn_event:
            return basestn_event['properties']

        return None

    @property
    def get_camera_rules(self):
        """Return the camera rules."""
        resource = "rules"
        rules_event = self.publish_and_get_event(resource)
        if rules_event:
            return rules_event['properties']

        return None

    @property
    def get_camera_schedule(self):
        """Return the schedule set for cameras."""
        resource = "schedule"
        schedule_event = self.publish_and_get_event(resource)
        if schedule_event:
            return schedule_event['properties']

        return None

    @property
    def is_motion_detection_enabled(self):
        """Return Boolean if motion is enabled."""
        return bool(self.mode == "armed" or self.get_camera_schedule['active'])

    @property
    def subscribe(self):
        """Subscribe this session with Arlo system."""
        self._get_event_stream()
        self._subscribe_myself()

    @property
    def unsubscribe(self):
        """Unsubscribe this session."""
        self._unsubscribe_myself()
        self._close_event_stream()

    @mode.setter
    def mode(self, mode):
        """Set Arlo camera mode.

        :param mode: arm, disarm
        """
        if mode not in ACTION_MODES.keys():
            return "Invalid mode"
        self.__run_action(
            method='SET',
            resource='modes',
            mode=mode,
            publish_response=True)
        self.update()

    def update(self):
        """Update object properties."""
        self._attrs = self._session.refresh_attributes(self.name)

# vim:sw=4:ts=4:et:
