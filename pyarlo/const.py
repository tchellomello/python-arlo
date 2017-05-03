"""Constants used by Python Arlo."""

# API Endpoints
API_URL = "https://arlo.netgear.com/hmsweb"

BILLING_ENDPOINT = API_URL + "/users/serviceLevel"
DEVICES_ENDPOINT = API_URL + "/users/devices"
FRIENDS_ENDPOINT = API_URL + "/users/friends"
LIBRARY_ENDPOINT = API_URL + "/users/library"
LOGIN_ENDPOINT = API_URL + "/login"
LOGOUT_ENDPOINT = API_URL + "/logout"
NOTIFY_ENDPOINT = API_URL + "/users/devices/notify/{0}"
PROFILE_ENDPOINT = API_URL + "/users/profile"
RESET_ENDPOINT = LIBRARY_ENDPOINT + "/reset"
RESET_CAM_ENDPOINT = RESET_ENDPOINT + "/?uniqueId={0}"
STREAM_ENDPOINT = API_URL + "/users/devices/startStream"

# number of days to preload video
PRELOAD_DAYS = 30

# define action modes
ACTION_MODES = {
    'armed': 'mode1',
    'disarmed': 'mode0',
    'custom': 'mode2',
    'schedule': 'true',
}

# define body used when executing an action
RUN_ACTION_BODY = {
    'action': 'set',
    'from': None,
    'properties': None,
    'publishResponse': 'true',
    'resource': 'modes',
    'to': None
}

# define body used for live_streaming
STREAMING_BODY = {
    'action': 'set',
    'from': None,
    'properties': {'activityState': 'startPositionStream'},
    'publishResponse': 'true',
    'resource': None,
    'to': None,
    'transId': "",
}

# vim:sw=4:ts=4:et:
