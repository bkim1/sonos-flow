import os
import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from app.services.api_sonos import SonosAPI


bp = Blueprint('flow_control', __name__, url_prefix='/flow')
SONOS_API = SonosAPI()
GROUP_IDS = {}
PLAYER_IDS = {}
FAVORITES = {}


@bp.route('/')
def setup_flow():
    """ Sets up the server to handle Flow control for the Sonos household
        authorized. Grabs the groups and favorites for the first household.
    """
    if not SONOS_API.set_tokens():
        return 'Please authorize first to get the access token'

    data, code = SONOS_API.get('households')
    if code < 200 or code > 300:
        return f'Error with getting household: {data}\nStatus Code: {code}'

    # Grab Household ID
    household_id = data['households'][0]['id']
    os.environ['HouseholdID'] = household_id

    # Get groups & player IDs
    data, code = SONOS_API.get(f'households/{household_id}/groups')
    if code < 200 or code > 300:
        return f'Error with getting groups: {data}\nStatus Code: {code}'
    
    for group in data['groups']:
        GROUP_IDS[group['name']] = group['id']
        PLAYER_IDS[group['name']] = group['playerIds']

    # Get favorites
    data, code = SONOS_API.get(f'households/{household_id}/favorites')
    if code < 200 or code > 300:
        return f'Error with getting favorites: {data}\nStatus Code: {code}'

    for item in data['items']:
        FAVORITES[item['name']] = item['id']

    return 'Flow has been setup!'


@bp.route('/favorites')
def get_favorites():
    """ Gets and returns the favorites for the authorized Sonos household """
    try:
        household_id = os.getenv('HouseholdID')
    except KeyError:
        return 'Need to setup the flow first!'
    else:
        data, code = SONOS_API.get(f'households/{household_id}/favorites')

        print(f'Data: {data}')
        print(f'Status Code: {code}')
        if code < 200 or code > 300:
            return f'Error with getting favorites: {data}\nStatus Code: {code}'

        for item in data['items']:
            FAVORITES[item['name']] = item['id']
        return {'message': 'Got the favorites!', 'data': data['items']}


@bp.route('/enter/<string:group>', methods=['GET', 'POST'],
          defaults={ 'favorite': None})
@bp.route('/enter/<string:group>/<string:favorite>', methods=['GET', 'POST'])
def enter_flow(group, favorite):
    """ Endpoint for when the user enters into the range of the speaker.
        
        If a favorite is not specified, then it attempts to resume whatever is
        paused or picks a random favorite to play if nothing was paused.
        Otherwise, plays the favorite for the group specified.

        Args:
            group: string representing the name of the group in the household

            favorite: string representing the name of the favorite in the
                      household
    """
    fav_provided = True
    try: 
        household_id = os.getenv('HouseholdID')
        group_id = GROUP_IDS[group]
        
        if favorite is None:
            favorite = random.choice(list(FAVORITES))
            fav_provided = False
        favorite_id = FAVORITES[favorite]
    except KeyError:
        return 'Need to setup the flow first!'
    else:
        if not fav_provided:
            # Attempt to play something already queued
            data, code = SONOS_API.post(f'groups/{group_id}/playback/play')
            if code >= 200 or code < 300:
                return 'Entered flow!'

        # Else, play favorites
        payload = {
            'favoriteId': favorite_id,
            'playOnCompletion': True,
        }
        data, code = SONOS_API.post(f'groups/{group_id}/favorites', payload=payload)
        if code < 200 or code > 300:
            return f'Error with starting playback: {data}\nStatus Code: {code}'

        print(f'Data: {data}')
        print(f'Status Code: {code}')
        return 'Entered flow!'


@bp.route('/exit/<string:group>', methods=['GET', 'POST'])
def exit_flow(group):
    """ Endpoint for when the user exits the range of the speaker. Pauses
        whatever is being played for the specified group.

        Args:
            group: string representing the name of the group in the household
    """
    try: 
        group_id = GROUP_IDS[group]
    except KeyError:
        return 'Need to setup the flow first!'
    else:
        data, code = SONOS_API.post(f'groups/{group_id}/playback/pause')
        if code < 200 or code > 300:
            return f'Error with pausing playback: {data}\nStatus Code: {code}'

        print(f'Data: {data}')
        print(f'Status Code: {code}')
        return 'Exited flow!'


@bp.route('/refresh')
def handle_refresh():
    """ Refreshes the access token for the Sonos API """
    resp = SONOS_API.refresh_tokens()

    if resp:
        return 'Refresh worked!'
    return 'Refresh Failed!'
