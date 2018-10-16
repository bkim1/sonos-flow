from urllib import parse
import os
import base64

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

import requests


bp = Blueprint('auth', __name__, url_prefix='/auth')


STATE = 'floState'
SONOS_AUTH_URL = 'https://api.sonos.com/login/v3/oauth'
LOGIN_REDIRECT_URI = parse.quote('https://sonos-flo.now.sh/auth/login-redirect', safe='')
LOGIN_LOCAL_REDIRECT_URI = parse.quote('http://localhost:5000/auth/login-redirect/1', safe='')
TOKEN_REDIRECT_URI = parse.quote('https://sonos-flo.now.sh/auth/token-redirect', safe='')
TOKEN_LOCAL_REDIRECT_URI = parse.quote('http://localhost:5000/auth/token-redirect', safe='')


# CLIENT_KEY = '89ca5e88-d049-42ad-9f13-3bbc839659f7'
# CLIENT_SECRET = 'f6d51a2a-7098-41aa-ad69-ba5ff024204c'


@bp.route('/login', defaults={'local': 0})
@bp.route('/login/<int:local>', methods=['GET'])
def authenticate(local):
    client_key = parse.quote(os.getenv("CLIENT_KEY"), safe='')
    redirect_uri = LOGIN_LOCAL_REDIRECT_URI if local else LOGIN_REDIRECT_URI

    auth_url = f'{SONOS_AUTH_URL}' \
               f'?client_id={client_key}' \
               f'&response_type=code' \
               f'&state={STATE}' \
               f'&scope=playback-control-all' \
               f'&redirect_uri={redirect_uri}'
    return redirect(auth_url)


@bp.route('/login-redirect', defaults={'local': 0}, methods=['GET'])
@bp.route('/login-redirect/<int:local>', methods=['GET'])
def handle_login_redirect(local):
    if STATE != request.args['state']:
        return 'Invalid Redirect... Wrong State'

    auth_code = request.args['code']
    print(auth_code)

    client_key, secret_key = os.getenv('CLIENT_KEY'), os.getenv('CLIENT_SECRET')

    # Base64 Encode 'ClientKey:SecretKey'
    key_pair = f'{client_key}:{secret_key}'
    encoded_keys = base64.b64encode(bytes(key_pair, 'utf-8'))
    encoded_keys_str = encoded_keys.decode('utf-8')

    redirect_uri = LOGIN_LOCAL_REDIRECT_URI if local else LOGIN_REDIRECT_URI

    # Set Headers & Data for request
    auth_url = f'{SONOS_AUTH_URL}/access'
    headers = {
        "Authorization": 'Basic %s' % encoded_keys_str,
        # 'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    print(headers)
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri
    }

    # Make POST request for Access Token
    resp = requests.post(auth_url, data=payload, headers=headers)
    print(f'Data: {resp.json()}')
    print(f'Status Code: {resp.status_code}')
    return 'Received Login Redirect!'
