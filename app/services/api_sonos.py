import os
import time
import base64

import requests


BASE_URL = 'https://api.ws.sonos.com/control/api/v1'
REFRESH_URL = 'https://api.sonos.com/login/v3/oauth/access'


class SonosAPI():
    """ Abstracting interactions with the Sonos API """
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_in = None
        self.token_created = None
    
    def set_tokens(self, tokens=None):
        try:
            if tokens is None:
                self.access_token = os.environ['AccessToken']
                self.refresh_token = os.environ['RefreshToken']
                self.expires_in = int(os.environ['ExpiresIn'])
                self.token_created = float(os.environ['TokenCreated'])
            else:
                self.access_token = tokens['AccessToken']
                self.refresh_token = tokens['RefreshToken']
                self.expires_in = tokens['ExpiresIn']
                self.token_created = tokens['TokenCreated']
        except KeyError:
            return False
        else:
            return True 
        
    def expired(self):
        return time.time() > self.token_created + self.expires_in

    def refresh_tokens(self):
        client_key, secret_key = os.getenv('CLIENT_KEY'), os.getenv('CLIENT_SECRET')

        # Base64 Encode 'ClientKey:SecretKey'
        key_pair = f'{client_key}:{secret_key}'
        encoded_keys = base64.b64encode(bytes(key_pair, 'utf-8'))
        encoded_keys_str = encoded_keys.decode('utf-8')

        headers = { 'Authorization': f'Basic {encoded_keys_str}' }
        payload = { 
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        resp = requests.post(REFRESH_URL, data=payload, headers=headers)
        json_data = resp.json()
        if resp.status_code < 200 or resp.status_code > 300:
            print(json_data)
            return False

        print(f'New Tokens: {json_data}')
        # Set tokens for class
        return self.set_tokens({
            'AccessToken': json_data['access_token'],
            'RefreshToken': json_data['refresh_token'],
            'ExpiresIn': json_data['expires_in'],
            'TokenCreated': time.time(),
        })

    def get(self, url, payload={}):
        if self.expired():
            resp = self.refresh_tokens()
            if not resp:
                return {'error': 'Need to reauthorize Flow'}, 401

        headers = { 'Authorization': f'Bearer {self.access_token}' }
        resp = requests.get(f'{BASE_URL}/{url}', headers=headers, params=payload)

        return resp.json(), resp.status_code

    def post(self, url, payload={}):
        if self.expired():
            resp = self.refresh_tokens()
            if not resp:
                return {'error': 'Need to reauthorize Flow'}, 401

        headers = { 'Authorization': f'Bearer {self.access_token}' }
        resp = requests.post(f'{BASE_URL}/{url}', headers=headers, json=payload)

        return resp.json(), resp.status_code
