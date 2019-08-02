import json

from project.statistics.pantheon import process_game, player_statistics_dict, add_difference

if __name__ == '__main__':
    # data = {
    #     "jsonrpc": "2.0",
    #     "method": "getLastGames",
    #     "params": {
    #         "eventIdList": [173],
    #         "limit": 200,
    #         "offset": 0
    #     },
    #     "id": "78bf5ab6-a7f1-4898-bd03-bb1902a50da7"
    # }
    # result = mjtop_request(data)
    # if result:
    #     games = result['games']

    # data = {
    #     'jsonrpc': '2.0',
    #     'method': 'getAllPlayers',
    #     'params': {
    #         'eventIdList': [173]
    #     },
    #     'id': '78bf5ab6-a7f1-4898-bd03-bb1902a50da7'
    # }
    # participating_players = mjtop_request(data)

    with open('games.json', encoding='utf-8') as outfile:
        games = json.load(outfile)

    with open('participating_players.json', encoding='utf-8') as outfile:
        participating_players = json.load(outfile)

    players = {}
    for game in games:
        print(game['players'], end=' ')
        diffs = process_game(game, participating_players)
        for player_id in diffs:
            if player_id not in players:
                players[player_id] = player_statistics_dict(player_id, participating_players)

            add_difference(
                base=players[player_id],
                diff=diffs[player_id]
            )
        print()

    print(players)