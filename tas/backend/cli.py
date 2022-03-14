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


commands = [
    ('Next Challenge', nextChallenge),
    ('Set Wallboard Players Max', wallboardPalyersMax)
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
