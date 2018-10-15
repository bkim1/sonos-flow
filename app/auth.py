from urllib import parse

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)


bp = Blueprint('auth', __name__, url_prefix='/auth')

SONOS_AUTH_URL = 'https://api.sonos.com/login/v3/oath'
CLIENT_ID = parse.quote('89ca5e88-d049-42ad-9f13-3bbc839659f7', safe='')
REDIRECT_URI = parse.quote('https://sonos-flo.now.sh/auth/redirect', safe='')


@bp.route('/login', methods=['GET'])
def authenticate():
    auth_url = f'{SONOS_AUTH_URL}?client_id={CLIENT_ID}' \
               f'&response_type=code' \
               f'&state=testState' \
               f'&scope=playback-control-all' \
               f'&redirect_uri={REDIRECT_URI}'
    return redirect(auth_url)


@bp.route('/login-redirect')
def handle_redirect():
    if request.method == 'POST':
        pass
    return 'Received callback!'
