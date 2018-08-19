# coding: utf-8
"""Generic Python Class file for Netgear Arlo Base Station module."""
import json
import threading
import logging
import time
import base64
import zlib
import sseclient
from pyarlo.const import (
    ACTION_BODY, SUBSCRIBE_ENDPOINT, UNSUBSCRIBE_ENDPOINT,
    FIXED_MODES, NOTIFY_ENDPOINT, RESOURCES)
from pyarlo.utils import assert_is_dict

_LOGGER = logging.getLogger(__name__)

REFRESH_RATE = 15


class ArloBaseStation(object):
    """Arlo Base Station module implementation."""

    def __init__(self, name, attrs, session_token, arlo_session,
                 refresh_rate=REFRESH_RATE):
        """Initialize Arlo Base Station object.

        :param name: Base Station name
        :param attrs: Attributes
        :param session_token: Session token passed by camera class
        :param arlo_session: PyArlo shared session
        :param refresh_rate: Attributes refresh rate. Defaults to 15
        """
        self.name = name
        self._attrs = attrs
        self._session = arlo_session
        self._session_token = session_token
        self._available_modes = None
        self._available_mode_ids = None
        self._camera_properties = None
        self._camera_extended_properties = None
        self._ambient_sensor_data = None
        self._last_refresh = None
        self._refresh_rate = refresh_rate
        self.__sseclient = None
        self.__subscribed = False
        self.__events = []
        self.__event_handle = None

        self._attrs = assert_is_dict(self._attrs)

    def __repr__(self):
        """Representation string of object."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    def thread_function(self):
        """Thread function."""

        self.__subscribed = True
        url = SUBSCRIBE_ENDPOINT + "?token=" + self._session_token

        data = self._session.query(url, method='GET', raw=True, stream=True)
        if not data or not data.ok:
            _LOGGER.debug("Did not receive a valid response. Aborting..")
            return None

        self.__sseclient = sseclient.SSEClient(data)

        try:
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
                        self.__event_handle.set()

        except TypeError as error:
            _LOGGER.debug("Got unexpected error: %s", error)
            return None

        return True

    def _get_event_stream(self):
        """Spawn a thread and monitor the Arlo Event Stream."""
        self.__event_handle = threading.Event()
        event_thread = threading.Thread(target=self.thread_function)
        event_thread.start()

    def _subscribe_myself(self):
        """Subscribe this base station for all events."""
        return self.publish(
            action='set',
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
        del self.__events[:]
        self.__event_handle.clear()

    def publish_and_get_event(self, resource):
        """Publish and get the event from base station."""
        l_subscribed = False
        this_event = None

        if not self.__subscribed:
            self._get_event_stream()
            self._subscribe_myself()
            l_subscribed = True

        status = self.publish(
            action='get',
            resource=resource,
            mode=None,
            publish_response=False)

        if status == 'success':
            i = 0
            while not this_event and i < 2:
                self.__event_handle.wait(5.0)
                self.__event_handle.clear()
                _LOGGER.debug("Instance %s resource: %s", str(i), resource)
                for event in self.__events:
                    if event['resource'] == resource:
                        this_event = event
                        self.__events.remove(event)
                        break
                i = i + 1

        if l_subscribed:
            self._unsubscribe_myself()
            self._close_event_stream()
            l_subscribed = False

        return this_event

    def publish(
            self,
            action='get',
            resource=None,
            camera_id=None,
            mode=None,
            publish_response=None,
            properties=None):
        """Run action.

        :param method: Specify the method GET, POST or PUT. Default is GET.
        :param resource: Specify one of the resources to fetch from arlo.
        :param camera_id: Specify the camera ID involved with this action
        :param mode: Specify the mode to set, else None for GET operations
        :param publish_response: Set to True for SETs. Default False
        """
        url = NOTIFY_ENDPOINT.format(self.device_id)

        body = ACTION_BODY.copy()

        if properties is None:
            properties = {}

        if resource:
            body['resource'] = resource

        if action == 'get':
            body['properties'] = None
        else:
            # consider moving this logic up a layer
            if resource == 'schedule':
                properties.update({'active': True})
            elif resource == 'subscribe':
                body['resource'] = "subscriptions/" + \
                        "{0}_web".format(self.user_id)
                dev = []
                dev.append(self.device_id)
                properties.update({'devices': dev})
            elif resource == 'modes':
                available_modes = self.available_modes_with_ids
                properties.update({'active': available_modes.get(mode)})
            elif resource == 'privacy':
                properties.update({'privacyActive': not mode})
                body['resource'] = "cameras/{0}".format(camera_id)

        body['action'] = action
        body['properties'] = properties
        body['publishResponse'] = publish_response

        body['from'] = "{0}_web".format(self.user_id)
        body['to'] = self.device_id
        body['transId'] = "web!{0}".format(self.xcloud_id)

        _LOGGER.debug("Action body: %s", body)

        ret = \
            self._session.query(url, method='POST', extra_params=body,
                                extra_headers={"xCloudId": self.xcloud_id})

        if ret and ret.get('success'):
            return 'success'

        return None

    # pylint: disable=invalid-name
    @property
    def device_id(self):
        """Return device_id."""
        if self._attrs is not None:
            return self._attrs.get('deviceId')
        return None

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
    def serial_number(self):
        """Return serial number."""
        if self._attrs is not None:
            return self._attrs.get('properties').get('serialNumber')
        return None

    @property
    def user_id(self):
        """Return userID."""
        if self._attrs is not None:
            return self._attrs.get('userId')
        return None

    @property
    def user_role(self):
        """Return userRole."""
        if self._attrs is not None:
            return self._attrs.get('userRole')
        return None

    @property
    def xcloud_id(self):
        """Return X-Cloud-ID attribute."""
        if self._attrs is not None:
            return self._attrs.get('xCloudId')
        return None

    @property
    def last_refresh(self):
        """Return last_refresh attribute."""
        return self._last_refresh

    @property
    def refresh_rate(self):
        """Return refresh_rate attribute."""
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value):
        """Override the refresh_rate attribute."""
        if isinstance(value, (int, float)):
            self._refresh_rate = value

    @property
    def available_modes(self):
        """Return list of available mode names."""
        if not self._available_modes:
            modes = self.available_modes_with_ids
            if not modes:
                return None
            self._available_modes = list(modes.keys())
        return self._available_modes

    @property
    def available_modes_with_ids(self):
        """Return list of objects containing available mode name and id."""
        if not self._available_mode_ids:
            all_modes = FIXED_MODES.copy()
            self._available_mode_ids = all_modes
            modes = self.get_available_modes()
            try:
                if modes:
                    # pylint: disable=consider-using-dict-comprehension
                    simple_modes = dict(
                        [(m.get("type", m.get("name")), m.get("id"))
                         for m in modes]
                    )
                    all_modes.update(simple_modes)
                    self._available_mode_ids = all_modes
            except TypeError:
                _LOGGER.debug("Did not receive a valid response. Passing..")
        return self._available_mode_ids

    @property
    def available_resources(self):
        """Return list of available resources."""
        return list(RESOURCES.keys())

    @property
    def mode(self):
        """Return current mode key."""

        if self.is_in_schedule_mode:
            return "schedule"

        resource = "modes"
        mode_event = self.publish_and_get_event(resource)
        if mode_event:
            properties = mode_event.get('properties')
            active_mode = properties.get('active')
            modes = properties.get('modes')
            if not modes:
                return None

            for mode in modes:
                if mode.get('id') == active_mode:
                    return mode.get('type') \
                        if mode.get('type') is not None else mode.get('name')
        return None

    @property
    def is_in_schedule_mode(self):
        """Returns True if base_station is currently on a scheduled mode."""
        resource = "schedule"
        mode_event = self.publish_and_get_event(resource)
        if mode_event and mode_event.get("resource", None) == "schedule":
            properties = mode_event.get('properties')
            return properties.get("active", False)
        return False

    def get_available_modes(self):
        """Return a list of available mode objects for an Arlo user."""
        resource = "modes"
        resource_event = self.publish_and_get_event(resource)
        if resource_event:
            properties = resource_event.get("properties")
            return properties.get("modes")

        return None

    @property
    def camera_properties(self):
        """Return _camera_properties"""
        if self._camera_properties is None:
            self.get_cameras_properties()
        return self._camera_properties

    def get_cameras_properties(self):
        """Return camera properties."""
        resource = "cameras"
        resource_event = self.publish_and_get_event(resource)
        if resource_event:
            self._last_refresh = int(time.time())
            self._camera_properties = resource_event.get('properties')

    def get_cameras_battery_level(self):
        """Return a list of battery levels of all cameras."""
        battery_levels = {}
        if not self.camera_properties:
            return None

        for camera in self.camera_properties:
            serialnum = camera.get('serialNumber')
            cam_battery = camera.get('batteryLevel')
            battery_levels[serialnum] = cam_battery
        return battery_levels

    def get_cameras_signal_strength(self):
        """Return a list of signal strength of all cameras."""
        signal_strength = {}
        if not self.camera_properties:
            return None

        for camera in self.camera_properties:
            serialnum = camera.get('serialNumber')
            cam_strength = camera.get('signalStrength')
            signal_strength[serialnum] = cam_strength
        return signal_strength

    @property
    def camera_extended_properties(self):
        """Return _camera_extended_properties."""
        if self._camera_extended_properties is None:
            self.get_camera_extended_properties()
        return self._camera_extended_properties

    def get_camera_extended_properties(self):
        """Return camera extended properties."""
        resource = 'cameras/{}'.format(self.device_id)
        resource_event = self.publish_and_get_event(resource)

        if resource_event is None:
            return None

        self._camera_extended_properties = resource_event.get('properties')
        return self._camera_extended_properties

    def get_speaker_muted(self):
        """Return whether or not the speaker is muted."""
        if not self.camera_extended_properties:
            return None

        speaker = self.camera_extended_properties.get('speaker')
        if not speaker:
            return None

        return speaker.get('mute')

    def get_speaker_volume(self):
        """Return the volume setting of the speaker."""
        if not self.camera_extended_properties:
            return None

        speaker = self.camera_extended_properties.get('speaker')
        if not speaker:
            return None

        return speaker.get('volume')

    def get_night_light_state(self):
        """Return the state of the night light (on/off)."""
        if not self.camera_extended_properties:
            return None

        night_light = self.camera_extended_properties.get('nightLight')
        if not night_light:
            return None

        if night_light.get('enabled'):
            return 'on'

        return 'off'

    def get_night_light_brightness(self):
        """Return the brightness (0-255) of the night light."""
        if not self.camera_extended_properties:
            return None

        night_light = self.camera_extended_properties.get('nightLight')
        if not night_light:
            return None

        return night_light.get('brightness')

    @property
    def properties(self):
        """Return the base station info."""
        resource = "basestation"
        basestn_event = self.publish_and_get_event(resource)
        if basestn_event:
            return basestn_event.get('properties')

        return None

    def get_cameras_rules(self):
        """Return the camera rules."""
        resource = "rules"
        rules_event = self.publish_and_get_event(resource)
        if rules_event:
            return rules_event.get('properties')

        return None

    def get_cameras_schedule(self):
        """Return the schedule set for cameras."""
        resource = "schedule"
        schedule_event = self.publish_and_get_event(resource)
        if schedule_event:
            return schedule_event.get('properties')

        return None

    @property
    def is_motion_detection_enabled(self):
        """Return Boolean if motion is enabled."""
        return self.mode == "armed"

    @property
    def ambient_sensor_data(self):
        """Return _ambient_sensor_data"""
        if self._ambient_sensor_data is None:
            self.get_ambient_sensor_data()
        return self._ambient_sensor_data

    @property
    def ambient_temperature(self):
        """Return the temperature property of the most recent
        history entry (in degrees celsius)"""
        return self.get_latest_ambient_sensor_statistic('temperature')

    @property
    def ambient_humidity(self):
        """Return the humidity property of the most recent
        history entry (in percent)"""
        return self.get_latest_ambient_sensor_statistic('humidity')

    @property
    def ambient_air_quality(self):
        """Return the air quality property of the most recent
        history entry (in VOC PPM)"""
        return self.get_latest_ambient_sensor_statistic('airQuality')

    def get_ambient_sensor_data(self):
        """Refresh ambient sensor history"""
        resource = 'cameras/{}/ambientSensors/history'.format(self.device_id)
        history_event = self.publish_and_get_event(resource)

        if history_event is None:
            return None

        properties = history_event.get('properties')

        self._ambient_sensor_data = \
            ArloBaseStation._decode_sensor_data(properties)

        return self._ambient_sensor_data

    @staticmethod
    def _decode_sensor_data(properties):
        """Decode, decompress, and parse the data from the history API"""
        b64_input = ""
        for s in properties.get('payload'):
            # pylint: disable=consider-using-join
            b64_input += s

        decoded = base64.b64decode(b64_input)
        data = zlib.decompress(decoded)
        points = []
        i = 0

        while i < len(data):
            points.append({
                'timestamp': int(1e3 * ArloBaseStation._parse_statistic(
                    data[i:(i + 4)], 0)),
                'temperature': ArloBaseStation._parse_statistic(
                    data[(i + 8):(i + 10)], 1),
                'humidity': ArloBaseStation._parse_statistic(
                    data[(i + 14):(i + 16)], 1),
                'airQuality': ArloBaseStation._parse_statistic(
                    data[(i + 20):(i + 22)], 1)
            })
            i += 22

        return points

    @staticmethod
    def _parse_statistic(data, scale):
        """Parse binary statistics returned from the history API"""
        i = 0
        for byte in bytearray(data):
            i = (i << 8) + byte

        if i == 32768:
            return None

        if scale == 0:
            return i

        return float(i) / (scale * 10)

    def get_latest_ambient_sensor_statistic(self, statistic):
        """Gets the most recent ambient sensor history entry"""
        if self._ambient_sensor_data is None:
            self.get_ambient_sensor_data()

        if self._ambient_sensor_data is None:
            return None

        return self._ambient_sensor_data[-1].get(statistic)

    def get_audio_playback_status(self):
        """Gets the current playback status and available track list"""
        resource = 'audioPlayback'
        return self.publish_and_get_event(resource)

    DEFAULT_TRACK_ID = '229dca67-7e3c-4a5f-8f43-90e1a9bffc38'

    def play_track(self, track_id=DEFAULT_TRACK_ID, position=0):
        """Plays a track at the given position."""
        self.publish(
            action='playTrack',
            resource='audioPlayback/player',
            publish_response=False,
            properties={'trackId': track_id, 'position': position}
        )

    def pause_track(self):
        """Pauses the currently playing track."""
        self.publish(
            action='pause',
            resource='audioPlayback/player',
            publish_response=False
        )

    def skip_track(self):
        """Skips to the next track in the playlist."""
        self.publish(
            action='nextTrack',
            resource='audioPlayback/player',
            publish_response=False
        )

    def set_music_loop_mode_continuous(self):
        """Sets the music loop mode to repeat the entire playlist."""
        self.publish(
            action='set',
            resource='audioPlayback/config',
            publish_response=False,
            properties={'config': {'loopbackMode': 'continuous'}}
        )

    def set_music_loop_mode_single(self):
        """Sets the music loop mode to repeat the current track."""
        self.publish(
            action='set',
            resource='audioPlayback/config',
            publish_response=False,
            properties={'config': {'loopbackMode': 'singleTrack'}}
        )

    def set_shuffle_on(self):
        """Sets playback to shuffle."""
        self.publish(
            action='set',
            resource='audioPlayback/config',
            publish_response=False,
            properties={'config': {'shuffleActive': True}}
        )

    def set_shuffle_off(self):
        """Sets playback to sequential."""
        self.publish(
            action='set',
            resource='audioPlayback/config',
            publish_response=False,
            properties={'config': {'shuffleActive': False}}
        )

    def set_volume(self, mute=False, volume=50):
        """Sets the music volume (0-100)"""
        self.publish(
            action='set',
            resource='cameras/{}'.format(self.device_id),
            publish_response=False,
            properties={'speaker': {'mute': mute, 'volume': volume}}
        )

    def set_night_light_on(self):
        """Turns on the night light."""
        self.publish(
            action='set',
            resource='cameras/{}'.format(self.device_id),
            publish_response=False,
            properties={'nightLight': {'enabled': True}}
        )

    def set_night_light_off(self):
        """Turns off the night light."""
        self.publish(
            action='set',
            resource='cameras/{}'.format(self.device_id),
            publish_response=False,
            properties={'nightLight': {'enabled': False}}
        )

    def set_night_light_brightness(self, brightness=200):
        """Sets the brightness of the night light (0-255)."""
        self.publish(
            action='set',
            resource='cameras/{}'.format(self.device_id),
            publish_response=False,
            properties={'nightLight': {'brightness': brightness}}
        )

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
        modes = self.available_modes
        if (not modes) or (mode not in modes):
            return
        self.publish(
            action='set',
            resource='modes' if mode != 'schedule' else 'schedule',
            mode=mode,
            publish_response=True)
        self.update()

    def set_camera_enabled(self, camera_id, is_enabled):
        """Turn Arlo camera On/Off.

        :param mode: True, False
        """
        self.publish(
            action='set',
            resource='privacy',
            camera_id=camera_id,
            mode=is_enabled,
            publish_response=True)
        self.update()

    def update(self):
        """Update object properties."""
        current_time = int(time.time())
        last_refresh = 0 if self._last_refresh is None else self._last_refresh

        if current_time >= (last_refresh + self._refresh_rate):
            self.get_cameras_properties()
            self.get_ambient_sensor_data()
            self.get_camera_extended_properties()
            self._attrs = self._session.refresh_attributes(self.name)
            self._attrs = assert_is_dict(self._attrs)
            _LOGGER.debug("Called base station update of camera properties: "
                          "Scan Interval: %s, New Properties: %s",
                          self._refresh_rate, self.camera_properties)

# vim:sw=4:ts=4:et:
