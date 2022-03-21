#!venv/bin/python
import sys
from helpers.config import get_config


def wallboardPalyersMax():
    from helpers.mongodb import get_wallboard_players_max, set_wallboard_players_max
    current = get_wallboard_players_max()
    selection = input(f"\nSet new wallboard players max ({current}): ")
    if not selection == "" and not int(selection) == current and int(selection) > 0:
        set_wallboard_players_max(int(selection))


def displayAdmin():
    from helpers.mongodb import get_display_admin, set_display_admin
    current = get_display_admin()
    selection = input(f"\nSet new display admin ({current}): ")
    if not selection == "" and not selection == current:
        set_display_admin(selection)


def displaySelfUrl():
    from helpers.mongodb import get_display_self_url, set_display_self_url
    current = get_display_self_url()
    selection = input(f"\nSet new display self url ({current}): ")
    if not selection == "" and not selection == current:
        set_display_self_url(selection)


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
    config = get_config('tmnf-server')
    sender = GbxRemote(config['host'], config['port'], config['user'], config['password'])
    sender.connect()

    selection = input("\nNext Challenge index (or empty for next Challenge in list): ")
    if not selection == "" and int(selection) >= 0:
        print(sender.callMethod('SetNextChallengeIndex', int(selection)))
    print(sender.callMethod('NextChallenge'))


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
    ('Set Wallboard Players Max', wallboardPalyersMax),
    ('Set Display Admin', displayAdmin),
    ('Set Display Self URL', displaySelfUrl),
    ('Clear DB', clearDB),
    ('Next Challenge', nextChallenge),
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
