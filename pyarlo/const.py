"""Constants used by Python Arlo."""

# API Endpoints
API_URL = "https://arlo.netgear.com/hmsweb"

BILLING_ENDPOINT = API_URL + "/users/serviceLevel"
DEVICES_ENDPOINT = API_URL + "/users/devices"
FRIENDS_ENDPOINT = API_URL + "/users/friends"
LOGIN_ENDPOINT = API_URL + "/login"
LOGOUT_ENDPOINT = API_URL + "/logout"
NOTIFY_ENDPOINT = API_URL + "/users/devices/notify/{0}"
PROFILE_ENDPOINT = API_URL + "/users/profile"

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
