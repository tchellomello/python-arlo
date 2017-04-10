"""Constants used by Python Arlo."""

# API Endpoints
API_URL = "https://arlo.netgear.com/hmsweb"

DEVICES_ENDPOINT = "/users/devices"
LOGIN_ENDPOINT = "/login"
LOGOUT_ENDPOINT = "/logout"
NOTIFY_ENDPOINT = "/users/devices/notify/{0}"

# default headers
HEADERS = {'Content-Type': 'application/json'}

# connection parameters
PARAMS = {'email': None, 'password': None}

# define action modes
ACTION_MODES = {
    'arm': 'mode1',
    'custom': 'mode',
    'disarm': 'mode0',
}


ACTION_STRUCT = {
    'from': None,
    'to': None,
    'action': 'set',
    'resource': 'modes',
    'publishResponse': 'true',
    'properties': None
}
