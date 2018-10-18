import os
import random
import time
import ast

from flask import (
    Blueprint, g, redirect, render_template, request, jsonify
)

from app.services.api_sonos import SonosAPI


bp = Blueprint('flow_control', __name__, url_prefix='/flow')
SONOS_API = SonosAPI()
GROUP_IDS_FILE = 'app/db/group_ids.txt'
PLAYER_IDS_FILE = 'app/db/player_ids.txt'
FAVORITES_FILE = 'app/db/favorites.txt'

@bp.route('/', methods=['GET'])
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
    
    set_saved_groups(data['groups'])
    set_saved_players(data['groups'])
    
    # Get favorites
    data, code = SONOS_API.get(f'households/{household_id}/favorites')
    if code < 200 or code > 300:
        return f'Error with getting favorites: {data}\nStatus Code: {code}'

    set_saved_favorites(data['items'])

    return jsonify({ 'message': 'Flow has been setup!' })


@bp.route('/favorites', methods=['GET'])
def get_favorites():
    """ Gets and returns the favorites for the authorized Sonos household """
    try:
        household_id = os.getenv('HouseholdID')
    except KeyError:
        return 'Need to setup the flow first!'
    else:
        data, code = SONOS_API.get(f'households/{household_id}/favorites')

        if code < 200 or code > 300:
            return f'Error with getting favorites: {data}\nStatus Code: {code}'

        set_saved_favorites(data['items'])
        return jsonify({'message': 'Got the favorites!', 'data': data['items']})


@bp.route('/enter/<string:group>', methods=['GET'],
          defaults={ 'favorite': None})
@bp.route('/enter/<string:group>/<string:favorite>', methods=['GET'])
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
        group_id = get_saved_groups()[group]
        favorites = get_saved_favorites()
        if favorite is None:
            favorite = random.choice(list(favorites))
            fav_provided = False
        favorite_id = favorites[favorite]
    except KeyError:
        return 'Need to setup the flow first!'
    else:
        if not fav_provided:
            # Attempt to play something already queued
            data, code = SONOS_API.post(f'groups/{group_id}/playback/play')
            if code >= 200 or code < 300:
                return jsonify({'message': 'Entered flow!', 'data': data})

        # Else, play favorites
        payload = {
            'favoriteId': favorite_id,
            'playOnCompletion': True,
        }
        data, code = SONOS_API.post(f'groups/{group_id}/favorites', payload=payload)
        if code < 200 or code > 300:
            return jsonify({ 'error': data, 'code': code, 'message': 'play' })

        return jsonify({'message': 'Entered flow!', 'data': data})


@bp.route('/exit/<string:group>', methods=['GET'])
def exit_flow(group):
    """ Endpoint for when the user exits the range of the speaker. Pauses
        whatever is being played for the specified group.

        Args:
            group: string representing the name of the group in the household
    """
    try: 
        group_id = get_saved_groups()[group]
    except KeyError:
        return 'Need to setup the flow first!'
    else:
        data, code = SONOS_API.post(f'groups/{group_id}/playback/pause')
        if code < 200 or code > 300:
            return jsonify({ 'error': data, 'code': code, 'message': 'pause' })

        return jsonify({'message': 'Exited flow!', 'data': data})


@bp.route('/continue/<string:group_from>/<string:group_to>', methods=['GET'])
def continue_flow(group_from, group_to):
    # Attempt to group together the speakers & then remove one of them
    try:
        groups, players = get_saved_groups(), get_saved_players()
        id_from, id_to = groups[group_from], groups[group_to]
        players_from, players_to = players[group_from], players[group_to]
    except KeyError as err:
        return jsonify({
            'error': str(err),
            'message': 'Need to setup the flow first!'
        })
    else:
        # Add new group to existing one
        payload = {
            'playerIdsToAdd': players_to,
            'playerIdsToRemove': []
        }
        data, code = SONOS_API.post(f'groups/{id_from}/groups/modifyGroupMembers', payload=payload)
        if code < 200 or code > 300:
            return jsonify({ 'error': data, 'code': code, 'message': 'add group' })

        # Update the group ids
        get_groups()
        groups = get_saved_groups()
        new_id_from = groups[f'{group_from} + 1']
        print(new_id_from)

        # Remove previous group
        payload = {
            'playerIdsToAdd': [],
            'playerIdsToRemove': players_from
        }
        data, code = SONOS_API.post(f'groups/{new_id_from}/groups/modifyGroupMembers', payload=payload)
        if code < 200 or code > 300:
            return jsonify({ 'error': data, 'code': code, 'message': 'remove group' })

        # Update the group ids again
        get_groups()
        return jsonify({
            'message': f'Transitioned from {group_from} to {group_to}',
            'data': data
        })



@bp.route('/groups', methods=['GET'])
def get_groups():
    try:
        household_id = os.getenv('HouseholdID')
    except KeyError:
        return 'Need to setup the flow first!'
    else:
        # Get groups & player IDs
        data, code = SONOS_API.get(f'households/{household_id}/groups')
        if code < 200 or code > 300:
            return jsonify({ 'error': data, 'code': code, 'message': 'get group' })
        
        # Update group info
        set_saved_groups(data['groups'])
        
        return jsonify({'data': data, 'message': 'Got the groups!'})


@bp.route('/refresh')
def handle_refresh():
    """ Refreshes the access token for the Sonos API """
    resp = SONOS_API.refresh_tokens()

    if resp:
        return 'Refresh worked!'
    return 'Refresh Failed!'


def get_saved_groups():
    groups = {}
    with open(GROUP_IDS_FILE, 'r') as f:
        for line in f:
            key, value = line.split(',,')
            groups[key] = value.rstrip()
    print(groups)
    return groups


def set_saved_groups(groups):
    with open(GROUP_IDS_FILE, 'w+') as f:
        for group in groups:
            f.write(f'{group["name"]},,{group["id"]}\n')
    return True


def get_saved_favorites():
    favorites = {}
    with open(FAVORITES_FILE, 'r') as f:
        for line in f:
            key, value = line.split(',,')
            favorites[key] = value.rstrip()
    print(favorites)
    return favorites


def set_saved_favorites(favorites):
    with open(FAVORITES_FILE, 'w+') as f:
        for item in favorites:
            f.write(f'{item["name"]},,{item["id"]}\n')
    return True


def get_saved_players():
    players = {}
    with open(PLAYER_IDS_FILE, 'r') as f:
        for line in f:
            key, value = line.split(',,')
            players[key] = ast.literal_eval(value.rstrip())
    print(players)
    return players        


def set_saved_players(groups):
    with open(PLAYER_IDS_FILE, 'w+') as f:
        for group in groups:
            f.write(f'{group["name"]},,{str(group["playerIds"])}\n')
    return True