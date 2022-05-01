#!venv/bin/python
import os
import sys
import argparse
import json
from helpers.GbxRemote import GbxRemote
os.chdir(os.path.dirname(os.path.realpath(__file__)))

parser = argparse.ArgumentParser(description='TMNF-TAS CLI')
parser.add_argument('--config', dest='config', action='store_true', default=False, help='Returns current configuration')
parser.add_argument('--enablemetrics', dest='enablemetrics', action='store_true', default=False, help='If set the TAS metrics endpoint is set to enabled')
args = parser.parse_args()


def wallboardPalyersMax():
    from helpers.mongodb import get_wallboard_players_max, set_wallboard_players_max
    current = get_wallboard_players_max()
    selection = input(f'\nSet new wallboard players max ({current}): ')
    if not selection == '' and not int(selection) == current and int(selection) > 0:
        set_wallboard_players_max(int(selection))


def wallboardChallengesMax():
    from helpers.mongodb import get_wallboard_challenges_max, set_wallboard_challenges_max
    current = get_wallboard_challenges_max()
    selection = input(f'\nSet new wallboard challenges max ({current}): ')
    if not selection == '' and not int(selection) == current and int(selection) > 0:
        set_wallboard_challenges_max(int(selection))


def displayAdmin():
    from helpers.mongodb import get_display_admin, set_display_admin
    current = get_display_admin()
    selection = input(f'\nSet new display admin ({current}): ')
    if not selection == '' and not selection == current:
        set_display_admin(selection)


def displaySelfUrl():
    from helpers.mongodb import get_display_self_url, set_display_self_url
    current = get_display_self_url()
    selection = input(f'\nSet new display self url ({current}): ')
    if not selection == '' and not selection == current:
        set_display_self_url(selection)


def downloadClient():
    from tqdm import tqdm
    import requests
    from helpers.mongodb import set_client_download_url
    url = 'http://files.trackmaniaforever.com/tmnationsforever_setup.exe'
    file_name = 'static/download/tmnf_client.exe'
    if os.path.isfile(file_name):
        selection = input('Client allready present. Delete and redownload it? (y/N): ').strip()
        if selection == 'y':
            os.remove(file_name)
            set_client_download_url()
        else:
            return
    new_url = input(f'Download URL ({url}): ').strip()
    if not new_url == '':
        url = new_url
    if not os.path.isdir('static/download'):
        os.makedirs('static/download')
    response = requests.get(url, stream=True)
    content_len = int(response.headers.get('Content-Length'))
    with open(file_name, 'wb') as handle, tqdm(total=content_len, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
        for data in response.iter_content(1024):
            pbar.update(len(data))
            handle.write(data)
    print('Setting client download url to new file')
    set_client_download_url('/download/tmnf_client.exe')


def clientDownloadURL():
    from helpers.mongodb import get_client_download_url, set_client_download_url
    if input('Disable Client Download URL? (y/N): ') == 'y':
        set_client_download_url()
        return
    current = get_client_download_url()
    if current is None:
        current = '/download/tmnf_client.exe'
    selection = input(f'\nSet new client download url ({current}): ')
    if selection == '':
        set_client_download_url(current)
    else:
        set_client_download_url(selection)


def clearDB():
    from helpers.mongodb import mongoDB
    if not input('Wipe all player, challenge and laptime data? (y/N): ').strip() == 'y':
        return
    mongoDB().challenges.drop()
    print('Wiped Challenges')
    mongoDB().players.drop()
    print('Wiped Players')
    mongoDB().laptimes.drop()
    print('Wiped Laptimes')
    mongoDB().laptimebackups.drop()
    print('Wiped Laptimebackups')
    mongoDB().bestlaptimes.drop()
    print('Wiped Bestlaptimes')
    mongoDB().rankings.drop()
    print('Wiped Rankings')
    mongoDB().utils.drop()
    print('Wiped Utils')
    if not input('Also wipe settings? (y/N): ').strip() == 'y':
        return
    mongoDB().settings.drop()
    print('Wiped Settings')


def nextChallenge():
    from helpers.config import get_config
    config = get_config('tmnf-server')
    sender = GbxRemote(config['host'], config['port'], config['user'], config['password'])
    sender.connect()

    selection = input('\nNext Challenge index (or empty for next Challenge in list): ')
    if not selection == '' and int(selection) >= 0:
        print(sender.callMethod('SetNextChallengeIndex', int(selection)))
    print(sender.callMethod('NextChallenge'))


def clearPlayerIP():
    from helpers.mongodb import mongoDB, player_get
    player_id = input('\nEnter player_id: ')
    player = player_get(player_id)
    if player is None:
        print('Invalid player_id!')
        return
    print(f"Player is currently assigned to IP: {player.get('ip')}")
    if input('Wipe it? (y/N): ').strip() == 'y':
        mongoDB().players.update_one({'_id': player_id}, {'$set': {'ip': None}})


def mergePlayers():
    from helpers.mongodb import player_get, player_merge
    from datetime import datetime
    p1 = input('PlayerID 1: ')
    p1 = player_get(player_id=p1)
    if p1 is None:
        print('Does not exist!')
        return
    print(f"Last Update: {datetime.fromtimestamp(p1['last_update']).isoformat()}\n")
    p2 = input('PlayerID 2: ')
    p2 = player_get(player_id=p2)
    if p2 is None:
        print('Does not exist!')
        return
    print(f"Last Update: {datetime.fromtimestamp(p2['last_update']).isoformat()}\n")
    p1, p2 = ((p1, p2) if p1['last_update'] > p2['last_update'] else (p2, p1))
    survivor = input(f"How survives? ({p1['_id']}): ")
    if survivor == '':
        pass
    elif not survivor == p1['_id'] and not survivor == p2['_id']:
        print('Invalid input!')
        return
    else:
        p1, p2 = ((p1, p2) if survivor == p1['_id'] else (p2, p1))
    print(f"{p2['_id']} is merged into {p1['_id']}")
    if input('Execute? (y/N): ') == 'y':
        player_merge(p1['_id'], p2['_id'])
        print('done')


def exit():
    sys.exit(0)


commands = [
    ('Set Wallboard Players Max', wallboardPalyersMax),
    ('Set Wallboard Challenges Max', wallboardChallengesMax),
    ('Set Display Admin', displayAdmin),
    ('Set Display Self URL', displaySelfUrl),
    ('Set Client Download URL', clientDownloadURL),
    ('Download/Provide TMNF Client', downloadClient),
    ('Clear DB', clearDB),
    ('Next Challenge', nextChallenge),
    ("Clear Player's IP", clearPlayerIP),
    ('Merge Players', mergePlayers),
    ('Exit', exit)
]

if args.config:
    from helpers.config import get_config
    print(json.dumps(get_config(), indent=2))
    sys.exit(0)

if args.enablemetrics:
    from helpers.config import get_config, set_config
    config = get_config('metrics')
    if not config.get('enabled', False):
        config['enabled'] = True
        set_config(config, 'metrics')
    sys.exit(0)

while True:
    index = 0
    for display, func in commands:
        print(f'{index} {display}')
        index += 1

    selection = int(input('\nSelect: '))
    if selection not in range(0, len(commands)):
        print('Invalid input!')
        sys.exit(1)

    commands[selection][1]()
    print()
