from optparse import OptionParser

from statistics.downloader import mjtop_request


def download_data(event_id):
    data = {
        'jsonrpc': '2.0',
        'method': 'getLastGames',
        'params': {
            'eventIdList': [173],
            'limit': 200,
            'offset': 0
        },
        'id': '78bf5ab6-a7f1-4898-bd03-bb1902a50da7'
    }

    result = mjtop_request(data)
    if result:
        games = result['games']

    data = {
        'jsonrpc': '2.0',
        'method': 'getAllPlayers',
        'params': {
            'eventIdList': [173]
        },
        'id': '78bf5ab6-a7f1-4898-bd03-bb1902a50da7'
    }
    participating_players = mjtop_request(data)


def main():
    parser = OptionParser()
    parser.add_option(
        '-e', '--event_id',
        type='int',
        help='Pantheon event ID',
    )

    opts, _ = parser.parse_args()
    event_id = opts.event_id

    if not event_id:
        parser.error('Pantheon event ID is not given')

    download_data(event_id)


if __name__ == '__main__':
    main()
