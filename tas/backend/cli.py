#!venv/bin/python
import sys
from helpers.config import get_config


def nextChallenge():
    config = get_config('tmnf-server')
    sender = GbxRemote(config['host'], config['port'], config['user'], config['password'])
    sender.connect()

    selection = input("\nNext Challenge index (or empty for next Challenge in list): ")
    if not selection == "" and int(selection) >= 0:
        print(sender.callMethod('SetNextChallengeIndex', int(selection)))
    print(sender.callMethod('NextChallenge'))


def wallboardPalyersMax():
    from helpers.mongodb import get_wallboard_players_max, set_wallboard_players_max
    current = get_wallboard_players_max()
    selection = input(f"\nSet new wallboard players max ({current}): ")
    if not selection == "" and not int(selection) == current and int(selection) > 0:
        set_wallboard_players_max(int(selection))


def clearPlayerIP():
    from helpers.mongodb import mongoDB, player_get
    player_id = input("\nEnter player_id: ")
    player = player_get(player_id)
    if player is None:
        print('Invalid player_id!')
        return
    print(f"Player is currently assigned to IP: {player.get('ip')}")
    if input('Wipe it? (y/N): ').strip() == 'y':
        mongoDB().players.update_one({'_id': player_id}, {'$set': {'ip': None}})


commands = [
    ('Next Challenge', nextChallenge),
    ('Set Wallboard Players Max', wallboardPalyersMax),
    ("Clear Player's IP", clearPlayerIP)
]

index = 0
for display, func in commands:
    print(f"{index} {display}")
    index += 1

selection = int(input("\nSelect: "))
if selection not in range(0, len(commands)):
    print("Invalid input!")
    sys.exit(1)

commands[selection][1]()
