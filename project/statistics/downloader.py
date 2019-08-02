import json
from typing import Dict

import requests


def mjtop_request(data: Dict) -> Dict:
    api_url = 'https://api.mjtop.net/'
    headers = {'Content-Type': 'application/json'}

    response = requests.post(
        api_url,
        headers=headers,
        data=json.dumps(data))

    if response.status_code == 200 and 'error' not in response.json().keys():
        result = response.json()['result']
    else:
        print(f'Error during requests to {api_url}')
        result = None

    return result


def load_games_from_mjtop(event_id: int):
    data = {
        "jsonrpc": "2.0",
        "method": "getLastGames",
        "params": {
            "eventIdList": [event_id],
            "limit": 1000,
            "offset": 0
        },
        "id": "78bf5ab6-a7f1-4898-bd03-bb1902a50da7"
    }
    result = mjtop_request(data)
    if result:
        return result['games']


def load_participating_players_from_mjtop(event_id: int):
    data = {
        'jsonrpc': '2.0',
        'method': 'getAllPlayers',
        'params': {
            'eventIdList': [event_id]
        },
        'id': '78bf5ab6-a7f1-4898-bd03-bb1902a50da7'
    }
    return mjtop_request(data)
