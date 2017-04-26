"""Constants used by Python Arlo."""

# API Endpoints
API_URL = "https://arlo.netgear.com/hmsweb"

BILLING_ENDPOINT = API_URL + "/users/serviceLevel"
DEVICES_ENDPOINT = API_URL + "/users/devices"
DISPLAY_ORDER_ENDPOINT = API_URL + "/users/devices/displayOrder"
FRIENDS_ENDPOINT = API_URL + "/users/friends"
LIBRARY_ENDPOINT = API_URL + "/users/library"
LOGIN_ENDPOINT = API_URL + "/login"
LOGOUT_ENDPOINT = API_URL + "/logout"
NOTIFY_ENDPOINT = API_URL + "/users/devices/notify/{0}"
PROFILE_ENDPOINT = API_URL + "/users/profile"

# default headers
HEADERS = {'Content-Type': 'application/json'}

# number of days to preload video
PRELOAD_DAYS = 30

# connection parameters
PARAMS = {'email': None, 'password': None}

# define action modes
ACTION_MODES = {
    'arm': 'mode1',
    'disarm': 'mode0',
}

# define body used when executing an action
RUN_ACTION_BODY = {
    'from': None,
    'to': None,
    'action': 'set',
    'resource': 'modes',
    'publishResponse': 'true',
    'properties': None
}

# vim:sw=4:ts=4:et:
