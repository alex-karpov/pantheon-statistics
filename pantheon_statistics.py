import requests
import json
import math
from typing import Dict, List, Tuple


class GameStatus():
    riichi_bets: int
    honba: int
    last_round: int
    next_round: int
    
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.riichi_bets = 0
        self.honba = 0
        self.last_round = 0
        self.next_round = 0       


def load_games_from_file(games_json):
    with open(games_json, encoding='utf-8') as outfile:
        return json.load(outfile)


def load_participating_players_from_file(participating_players_json):
    with open(participating_players_json, encoding='utf-8') as outfile:
        return json.load(outfile)


def mjtop_request(data: Dict) -> Dict:
    api_url = 'https://api.mjtop.net/'
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(api_url,
                             headers=headers, 
                             data=json.dumps(data))
    
    if (response.status_code == 200 and 
        'error' not in response.json().keys()):

        result = response.json()['result']
    else:
        print(f'Error during requests to {api_url}')    
        result = None
        
    return result


def load_games_from_mjtop(event_id):
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


def load_participating_players_from_mjtop(event_id):
    data = {
        'jsonrpc': '2.0',
         'method': 'getAllPlayers',
         'params': {
             'eventIdList': [event_id]
         },
         'id': '78bf5ab6-a7f1-4898-bd03-bb1902a50da7'
    }
    return mjtop_request(data)


def get_player_by_id(player_id: int, participating_players: Dict) -> Dict:
    if not player_id:
        return {}
    result = {
        'player_id': player_id
    }
    
    for player in participating_players:
        if player['id'] == player_id:
            if 'display_name' in player:
                result['player_name'] = player['display_name']
            if 'team_name' in player:
                result['player_team'] = player['team_name']
            if 'tenhou_id' in player:
                result['player_tenhou_id'] = player['tenhou_id']
            break
    
    return result


def player_statistics_dict(player_id: int = 0, participating_players: Dict = None) -> Dict:
    player_statistics = get_player_by_id(player_id, participating_players)
    
    player_statistics.update({
        'num_games': 0, # Количество сыгранных ханчанов (туров)
        'num_games_aborted': 0, # Количество прерванных ханчанов (прерванных по времени или по другим причинам)
        
        'num_rounds': 0, # Количество сыгранных раздач
        'num_rounds_dealer': 0, # Количество раздач, сыгранных на дилере
        'num_dealer_wins': 0, # Количество побед (рон или цумо) на дилере
        
        'num_wins': 0, # Количество побед по рон и цумо
        'num_wins_ron': 0, # Количество побед по рон, включая дабл- и трипл-рон
        'num_wins_double_ron': 0, # Количество побед по дабл-рон
        'num_wins_triple_ron': 0, # Количество побед по трипл-рон
        'num_wins_tsumo': 0, # Количество побед по цумо
        'num_wins_open_hand': 0, # Количество побед с открытой рукой

        'num_draws': 0, # Количество ничьих
        'num_draws_tempai': 0, # Количество темпаев при ничьей
        'num_draws_noten': 0, # Количество нотен при ничьей
        'num_abort': 0, # Количество пересдач (абортивных ничьих)
        'num_chombo': 0, # Количество штрафов чомбо
        
        'num_feeds': 0, # Количество набросов в рон
        'num_feeds_under_riichi': 0, # Количество набросов в рон из-за риичи
        'num_tsumo_feeds': 0, # Количество выплат по цумо, включая выплаты по цумо на дилере
        'num_tsumo_feeds_dealer': 0, # Количество выплат по цумо будучи на дилере
        
        'riichi_bets_wins': 0, # Количество выигранных риичи-палочек
        'riichi_bets_lost': 0, # Количество потерянных риичи-палочек

        'doras': 0, # Количество дор в собранных руках (учитываются все виды дор)
        'doras_normal': 0, # Количество обычных дор в собранных руках
        'doras_uradora': 0, # Количество урадор в собранных руках
        'doras_kandora': 0, # Количество кандор в собранных руках
        'doras_kanuradora': 0, # Количество канурадор в собранных руках
        'doras_akadora': 0, # Количество акадор в собранных руках

        'gains_ron': 0, # Выиграно очков по рон, включая выигрыши на дилере, включая хонбу и чужие риичи-палки
        'gains_tsumo': 0, # Выиграно очков по цумо, включая выигрыши на дилере, включая хонбу и чужие риичи-палки
        'gains_ron_dealer': 0, # Выиграно очков по рон на дилере, включая хонбу и чужие риичи-палки
        'gains_tsumo_dealer': 0, # Выиграно очков по цумо на дилере, включая хонбу и чужие риичи-палки
        'gains_tempai': 0, # Выиграно очков при ничьих
        'losses_ron': 0, # Выплачено очков за набросы в рон, включая хонбу
        'losses_tsumo': 0, # Выплачено очков по цумо, включая выплаты на дилере, включая хонбу
        'losses_tsumo_dealer': 0, # Выплачено очков по цумо на дилере, включая хонбу
        'losses_noten': 0, # Выплачено очков за нотен при ничьих

        'yaku': {} # Количество собранных яку
    })
    
    player_statistics.update(
        player_payment_dict())
    
    return player_statistics


def player_payment_dict():
    payment_dict = {
        'gains_ron': 0, # Выиграно очков по рон, включая выигрыши на дилере, включая хонбу и чужие риичи-палки
        'gains_tsumo': 0, # Выиграно очков по цумо, включая выигрыши на дилере, включая хонбу и чужие риичи-палки
        'gains_ron_dealer': 0, # Выиграно очков по рон на дилере, включая хонбу и чужие риичи-палки
        'gains_tsumo_dealer': 0, # Выиграно очков по цумо на дилере, включая хонбу и чужие риичи-палки
        'gains_tempai': 0, # Выиграно очков при ничьих
        'losses_ron': 0, # Выплачено очков за набросы в рон, включая хонбу
        'losses_tsumo': 0, # Выплачено очков по цумо, включая выплаты на дилере, включая хонбу
        'losses_tsumo_dealer': 0, # Выплачено очков по цумо на дилере, включая хонбу
        'losses_noten': 0, # Выплачено очков за нотен при ничьих
    }
    return payment_dict


def get_dealer_id(round_index: int, game: Dict) -> int:
    return game['players'][(round_index - 1) % 4]


def get_atamahane_winner(players: List[int], winners: List[int], loser: int):
    look_winner = False
    for player_id in players * 2:
        if player_id == loser:
            look_winner = True
        if look_winner and player_id in winners:
            return player_id


def parse_ids(ids_list: str) -> List[int]:
    """
    Get ids list (int numbers) from comma separated string
    '' -> []
    '31' -> [31]
    '41,54,76' -> [41, 54, 76]
    """
    if not ids_list:
        return []
    else:
        return list(map(lambda s: int(s), ids_list.split(',')))

    
def add_difference(base: Dict, diff: Dict) -> None:
    for key in diff:
        if key in ('player_id', 'player_name', 'player_team', 'player_tenhou_id'):
            pass
        elif key is 'yaku':
            add_difference(base.get(key, {}), diff[key])
        else:
            base[key] = base.get(key, 0) + diff[key]


def _calculate_payments(round_: Dict, status: GameStatus, game: Dict) -> Dict[str, int]:
    winner_id = round_.get('winner_id', 0)

    outcome = round_.get('outcome', 'ron') == 'ron'
    
    if outcome in ('ron', 'tsumo'):
        payment = _calculate_points(round_, status, game)
        if winner_id == player_id:
            payment['gains_ron'] = payment['gains_ron_dealer']
            payment['gains_tsumo'] = payment['gains_tsumo_dealer']
        
        
    elif outcome == 'draw':
        payment = _calculate_points_draw(round_, status, game)
    else:
        payment = player_payment_dict()
        
    return payment
    

def _calculate_points_draw(round_: Dict, status: GameStatus, game: Dict) -> Dict[str, int]:
    payment = player_payment_dict()
    tempai_count = len(parse_ids(round_.get('tempai', '')))
    
    if tempai_count == 1:
        payment['gains_tempai'] = 3000
        payment['losses_noten'] = 1000
    elif tempai_count == 2:
        payment['gains_tempai'] = 1500
        payment['losses_noten'] = 1500
    elif tempai_count == 3:
        payment['gains_tempai'] = 1000
        payment['losses_noten'] = 3000
    
    return payment


def _round_up_to_100(number: int):
    return int(math.ceil(number / 100.0)) * 100


def _calculate_points(round_: Dict, status: GameStatus, game: Dict) -> Dict[str, int]:
    # TODO: Pao rule
    # TODO: Tournament rules
    payment = player_payment_dict()
    
    han = round_['han']
    fu = round_.get('fu', 0)
    
    if 0 < han < 5:
        base_points = fu * 2 ** (2 + han)
        rounded = _round_up_to_100(base_points)
        double_rounded = _round_up_to_100(2 * base_points)
        times_four_rounded = _round_up_to_100(4 * base_points)
        times_six_rounded = _round_up_to_100(6 * base_points)
        
        if base_points >= 2000:
            rounded = 2000
            double_rounded = 2 * rounded
            times_four_rounded = 4 * rounded
            times_six_rounded = 6 * rounded
    else:
        if han < 0:
            rounded = abs(han * 8000)
        elif han >= 13:
            rounded = 8000
        elif han >= 11:
            rounded = 6000
        elif han >= 8:
            rounded = 4000
        elif han >= 6:
            rounded = 3000
        else:
            rounded = 2000
        double_rounded = 2 * rounded
        times_four_rounded = 4 * rounded
        times_six_rounded = 6 * rounded        
    
    payment['gains_ron'] = times_four_rounded
    payment['gains_tsumo'] = times_four_rounded
    payment['gains_ron_dealer'] = times_six_rounded
    payment['gains_tsumo_dealer'] = times_six_rounded
    payment['losses_ron'] = times_four_rounded
    payment['losses_tsumo'] = rounded
    payment['losses_tsumo_dealer'] = double_rounded

    return payment


def _process_win(round_: Dict, status: GameStatus, game: Dict) -> Dict[str, int]:
    diff = player_statistics_dict()
    player_id = round_.get('winner_id', 0)
    riichi_bets = parse_ids(round_.get('riichi_bets', ''))
    
    diff['num_wins'] = 1

    bets_win = status.riichi_bets
    bets_win += len(riichi_bets)
    if player_id in riichi_bets:
        bets_win -= 1
    diff['riichi_bets_wins'] = bets_win
    status.riichi_bets = 0    
    
    if round_.get('outcome', 'ron') == 'ron':
        diff['num_wins_ron'] = 1
        
    else:
        diff['num_wins_tsumo'] = 1

    if round_.get('open_hand', False):
        diff['num_wins_open_hand'] = 1


    diff['doras_normal'] = round_.get('dora', 0)
    diff['doras_uradora'] = round_.get('uradora', 0)
    diff['doras_kandora'] = round_.get('kandora', 0)
    diff['doras_kanuradora'] = round_.get('kanuradora', 0)
    diff['doras_akadora'] = round_.get('akadora', 0)

    diff['doras'] = sum([
        diff['doras_normal'],
        diff['doras_uradora'],
        diff['doras_kandora'],
        diff['doras_kanuradora'],
        diff['doras_akadora']])

    yaku_list = parse_ids(round_.get('yaku', ''))
    diff['yaku'] = {yaku_id: 1 for yaku_id in yaku_list}
    
    return diff


def process_ron_outcome(round_: Dict, status: GameStatus, game: Dict) -> Tuple[Dict[int, Dict[str, int]], GameStatus]:
    diffs = {}
    for player_id in game['players']:
        diffs[player_id] = player_statistics_dict()
    
    dealer_id = get_dealer_id(round_.get('round_index', 1), game)
    winner_id = round_.get('winner_id', 0)
    loser_id = round_.get('loser_id', 0)
    riichi_bets = parse_ids(round_.get('riichi_bets', ''))
    payment = _calculate_points(round_, status, game)
    
    for player_id, diff in diffs.items():
        # Common part
        diff['num_rounds'] = 1
        
        # Dealer part
        if player_id == dealer_id:
            diff['num_rounds_dealer'] = 1
            if player_id == winner_id:
                diff['num_dealer_wins'] = 1

        # Winner part
        if player_id == winner_id:
            add_difference(diff, _process_win(round_, status, game))
            diff['gains_ron'] += 300 * status.honba
            diff['gains_ron'] += 1000 * diff['riichi_bets_wins']
            if player_id == dealer_id:
                diff['gains_ron'] += payment['gains_ron_dealer']
                diff['gains_ron_dealer'] = diff['gains_ron']
            else:
                diff['gains_ron'] += payment['gains_ron']

            # Not winner part
        else:
            if player_id in riichi_bets:
                diff['riichi_bets_lost'] = 1
                
        # Loser part
        if player_id == loser_id:
            diff['num_feeds'] = 1
            if player_id in riichi_bets:
                diff['num_feeds_under_riichi'] = 1
            
            diff['losses_ron'] += 300 * status.honba
            if winner_id == dealer_id:
                diff['losses_ron'] += payment['gains_ron_dealer']
            else:
                diff['losses_ron'] += payment['gains_ron']


    status.riichi_bets = 0
    status.last_round = round_.get('round_index', 1)
    if winner_id == dealer_id:
        status.honba += 1
        status.next_round = status.last_round
    else:
        status.honba = 0
        status.next_round = status.last_round + 1
            
    return diffs, status


def process_multiron_outcome(round_: Dict, status: GameStatus, game: Dict) -> Tuple[Dict[int, Dict[str, int]], GameStatus]:
    diffs = {}
    for player_id in game['players']:
        diffs[player_id] = player_statistics_dict()
    
    dealer_id = get_dealer_id(round_.get('round_index', 1), game)
    winner_ids = list([win.get('winner_id', 0) for win in round_['wins']])
    loser_id = round_.get('loser_id', 0)
    riichi_bets = parse_ids(round_.get('riichi_bets', ''))
    atamahane_winner_id = get_atamahane_winner(game['players'], winner_ids, loser_id)

    diffs[loser_id]['num_feeds'] = 1

    for player_id, diff in diffs.items():
        # Common part
        diff['num_rounds'] = 1
        
        # Dealer part
        if player_id == dealer_id:
            diff['num_rounds_dealer'] = 1
            if player_id in winner_ids:
                diff['num_dealer_wins'] = 1

    # Обработка риичи-палочек. Победителю возвращается его риичи-палочка, 
    # остальные палочки отходят по правилу атамахане     
    bets_on_table = status.riichi_bets
    bets_on_table += len(riichi_bets)
    for player_id in riichi_bets:
        if player_id in winner_ids:
            diffs[player_id]['riichi_bets_wins'] = 1
            bets_on_table -= 1
        else:
            diffs['riichi_bets_lost'] = 1
        if player_id == loser_id:
            diffs[loser_id]['num_feeds_under_riichi'] = 1
    diffs[atamahane_winner_id]['riichi_bets_wins'] += bets_on_table

    for win in round_['wins']:
        winner_id = win.get('winner_id', 0)
        
        multi_ron = round_.get('multi_ron', 0)
        if multi_ron == 2:
            diffs[winner_id]['num_wins_double_ron'] = 1
        if multi_ron == 3:
            diffs[winner_id]['num_wins_triple_ron'] = 1
        
        add_difference(
            diffs[winner_id],
            _process_win(win, status, game))
        
        payment = _calculate_points(win, status, game)
        diffs[winner_id]['gains_ron'] += 300 * status.honba
        diffs[winner_id]['gains_ron'] += 1000 * diffs[winner_id]['riichi_bets_wins']
        diffs[loser_id]['losses_ron'] += 300 * status.honba
        if winner_id == dealer_id:
            diffs[winner_id]['gains_ron'] += payment['gains_ron_dealer']
            diffs[winner_id]['gains_ron_dealer'] += diffs[winner_id]['gains_ron']
            diffs[loser_id]['losses_ron'] += payment['gains_ron_dealer']
        else:
            diffs[winner_id]['gains_ron'] += payment['gains_ron']
            diffs[loser_id]['losses_ron'] += payment['gains_ron']

    status.riichi_bets = 0
    status.last_round = round_.get('round_index', 1)
    if dealer_id in winner_ids:
        status.honba += 1
        status.next_round = status.last_round
    else:
        status.honba = 0
        status.next_round = status.last_round + 1
            
    return diffs, status


def process_tsumo_outcome(round_: Dict, status: GameStatus, game: Dict) -> Tuple[Dict[int, Dict[str, int]], GameStatus]:
    diffs = {}
    for player_id in game['players']:
        diffs[player_id] = player_statistics_dict()
    
    dealer_id = get_dealer_id(round_.get('round_index', 1), game)
    winner_id = round_.get('winner_id', 0)
    riichi_bets = parse_ids(round_.get('riichi_bets', ''))
    payment = _calculate_points(round_, status, game)
    
    for player_id, diff in diffs.items():
        # Common part
        diff['num_rounds'] = 1
        
        # Dealer part
        if player_id == dealer_id:
            diff['num_rounds_dealer'] = 1
            if player_id == winner_id:
                diff['num_dealer_wins'] = 1

        # Winner part
        if player_id == winner_id:
            add_difference(diff, _process_win(round_, status, game))
            diff['gains_tsumo'] += 300 * status.honba
            diff['gains_tsumo'] += 1000 * diff['riichi_bets_wins']
            if player_id == dealer_id:
                diff['gains_tsumo'] += payment['gains_tsumo_dealer']
                diff['gains_tsumo_dealer'] = diff['gains_tsumo']
            else:
                diff['gains_tsumo'] += payment['gains_tsumo']
        
        # Not winner part
        else:
            if player_id in riichi_bets:
                diff['riichi_bets_lost'] = 1
            diff['num_tsumo_feeds'] = 1
            diff['losses_tsumo'] += 100 * status.honba
            if player_id == dealer_id:
                diff['num_tsumo_feeds_dealer'] = 1
                diff['losses_tsumo'] += payment['losses_tsumo_dealer']
                diff['losses_tsumo_dealer'] = diff['losses_tsumo']
            else:
                diff['losses_tsumo'] += payment['losses_tsumo']

    status.riichi_bets = 0
    status.last_round = round_.get('round_index', 1)
    if winner_id == dealer_id:
        status.honba += 1
        status.next_round = status.last_round
    else:
        status.honba = 0
        status.next_round = status.last_round + 1

    return diffs, status


def process_draw_outcome(round_: Dict, status: GameStatus, game: Dict) -> Tuple[Dict[int, Dict[str, int]], GameStatus]:
    diffs = {}
    for player_id in game['players']:
        diffs[player_id] = player_statistics_dict()
    
    dealer_id = get_dealer_id(round_.get('round_index', 1), game)
    tempai_ids = parse_ids(round_.get('tempai', ''))
    riichi_bets = parse_ids(round_.get('riichi_bets', ''))
    payment = _calculate_points_draw(round_, status, game)
    
    for player_id, diff in diffs.items():
        # Common part
        diff['num_rounds'] = 1
        diff['num_draws'] = 1
        
        # Dealer part
        if player_id == dealer_id:
            diff['num_rounds_dealer'] = 1

        # Tempai part
        if player_id in tempai_ids:
            diff['num_draws_tempai'] = 1
            diff['gains_tempai'] += payment['gains_tempai']
        # Noten part
        else:
            diff['num_draws_noten'] = 1
            diff['losses_noten'] += payment['losses_noten']
            
        # Riichi bets
        if player_id in riichi_bets:
            diff['riichi_bets_lost'] = 1

    status.riichi_bets += len(riichi_bets)
    status.honba += 1
    status.last_round = round_.get('round_index', 1)
    if dealer_id in tempai_ids:
        status.next_round = status.last_round
    else:
        status.next_round = status.last_round + 1

    return diffs, status


def process_abort_outcome(round_: Dict, status: GameStatus, game: Dict) -> Tuple[Dict[int, Dict[str, int]], GameStatus]:
    diffs = {}
    for player_id in game['players']:
        diffs[player_id] = player_statistics_dict()
    
    dealer_id = get_dealer_id(round_.get('round_index', 1), game)
    riichi_bets = parse_ids(round_.get('riichi_bets', ''))
    
    for player_id, diff in diffs.items():
        # Common part
        diff['num_rounds'] = 1
        diff['num_abort'] = 1
        
        # Dealer part
        if player_id == dealer_id:
            diff['num_rounds_dealer'] = 1

        # Riichi bets
        if player_id in riichi_bets:
            diff['riichi_bets_lost'] = 1

    status.riichi_bets += len(riichi_bets)
    status.honba += 1
    status.last_round = round_.get('round_index', 1)
    status.next_round = status.last_round

    return diffs, status


def process_chombo_outcome(round_: Dict, status: GameStatus, game: Dict) -> Tuple[Dict[int, Dict[str, int]], GameStatus]:
    """
    Чомбо учитывается как обычный раунд: несмотря на то, что в обычных играх 
    чомбо это прерванная без возможности продолжать раздача и следующая раздача --
    переигрывание предыдущей, испорченной, на турнирах время на чомбо-раунд 
    не компенсируется. К тому же, в статистике пантеона чомбо-раунд учитывается как
    сыгранная раздача. Риичи-ставки не учитываю: они не являются ни проигранными, 
    ни выигранными, а возвращаются владельцу.
    """
    diffs = {}
    for player_id in game['players']:
        diffs[player_id] = player_statistics_dict()
    
    # Chombo is round too, but discussable
    dealer_id = get_dealer_id(round_.get('round_index', 1), game)
    loser_id = round_.get('loser_id', 0)
    
    for player_id, diff in diffs.items():
        # Common part
        diff['num_rounds'] = 1

        if player_id == loser_id:
            diff['num_chombo'] = 1
        
        # Dealer part
        if player_id == dealer_id:
            diff['num_rounds_dealer'] = 1


    status.last_round = round_.get('round_index', 1)
    status.next_round = status.last_round

    return diffs, status


outcome_processors = {
    'ron': process_ron_outcome,
    'multiron': process_multiron_outcome,
    'tsumo': process_tsumo_outcome,
    'draw': process_draw_outcome,
    'abort': process_abort_outcome,
    'chombo': process_chombo_outcome,
}


def process_game(game: Dict, participating_players: Dict) -> Dict[int, Dict[str, int]]:
    status = GameStatus()

    game_diffs = {}
    for player_id in game['players']:
        game_diffs[player_id] = player_statistics_dict(player_id, participating_players)

    diffs = {}
    for round_ in game['rounds']:
        diffs, status = outcome_processors[round_['outcome']](round_, status, game)
        
        for player_id in diffs:
            add_difference(
                base=game_diffs[player_id],
                diff=diffs[player_id]
            )
    
    for player_id in diffs:
        game_diffs[player_id]['num_games'] = 1
        if status.next_round <= 8:
            game_diffs[player_id]['num_games_aborted'] = 1
    
    return game_diffs


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


