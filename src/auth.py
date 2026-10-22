from . import config
from . import utils
from . import cryption
import json
import sys
from . import user_session as user

def register_user():
    """Registers a new user with the server."""
    url = f"{config.get_api_url()}/users/register"
    user_data = build_user_data()

    # Set initial session key
    k = cryption.create_from_key("vuyWQSjlknpJF54ib36txVse")
    config.USER_INFO['session_key'] = k

    config.update_request_headers()
    encoded_data = cryption.encrypt(k, user_data)
    response = config.SESSION.post(url, json={"encoded": True, "data": encoded_data.decode('utf-8')})

    if response.ok:
        handle_registration_response(response.json())
        print('Account created successfully.')
    else:
        print(response.status_code)
        print('Error during registration.')
        sys.exit(0)

def login_user():
    """Logs in a user and updates session details."""
    url = f"{config.get_api_url()}/users/sessions"
    user_data = build_user_data()

    # Set initial session key
    k = cryption.create_from_key("vuyWQSjlknpJF54ib36txVse")
    config.USER_INFO['session_key'] = k

    encoded_data = cryption.encrypt(k, user_data)
    response = config.SESSION.post(url, json={"encoded": True, "data": encoded_data.decode('utf-8')})

    if response.ok:
        handle_login_response(response.json())
        print('Sign-in complete.')
    else:
        print('Login failed.')
        sys.exit(0)

def build_user_data():
    """Builds user data for sending to the server."""
    config.USER_INFO["uuid"] = config.USER_INFO["uuid"] or utils.generate_uuid()
    config.USER_INFO["adid"] = config.USER_INFO["adid"] or utils.generate_gaid()
    config.USER_INFO["udid"] = config.USER_INFO["udid"] or utils.generate_idfa()

    fields = {
        "uuid": config.USER_INFO["uuid"],
        "country_code": "CA",
        "currency_unit": "CAD",
        "idfa": "00000000-0000-0000-0000-000000000000",
        "locale": "en",
    }

    if config.USER_INFO['platform'] == 'android':
        fields["adid"] = config.USER_INFO["adid"]
    elif config.USER_INFO['platform'] == 'ios':
        fields["udid"] = config.USER_INFO["udid"]

    return json.dumps(fields)

def handle_registration_response(data):
    """Processes server response after registration."""
    
    data_string = cryption.decrypt(config.USER_INFO['session_key'], data['data'])
    data_string = json.loads(data_string.value.decode('utf-8'))
    config.USER_INFO["bq159_key"] = data_string["bq159_key"]
    config.USER_INFO["session_key"] = cryption.create_from_key(config.USER_INFO["bq159_key"])
    config.USER_INFO["sakura_session"] = data_string["session_id"]
    config.update_request_headers(config.USER_INFO["sakura_session"])

def handle_login_response(data):
    """Processes server response after login."""
    
    data_string = cryption.decrypt(config.USER_INFO['session_key'], data['data'])
    data_string = json.loads(data_string.value.decode('utf-8'))
    config.USER_INFO["bq159_key"] = data_string["bq159_key"]
    config.USER_INFO["session_key"] = cryption.create_from_key(config.USER_INFO["bq159_key"])
    config.USER_INFO["sakura_session"] = data_string["session_id"]
    config.update_request_headers(config.USER_INFO["sakura_session"])
    
    user.user_login_bonuses()
    user.user_login_stamp()
