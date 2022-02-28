#!venv/bin/python

import argparse
from helpers.GbxRemote import GbxRemote
from helpers.config import get_config

parser = argparse.ArgumentParser(description="Change to next Challenge")
parser.add_argument('--challenge', '-c', dest='challenge', type=int, required=False, default=-1, help='Challenge-Index to change to')
args = parser.parse_args()

config = get_config('tmnf-server')
sender = GbxRemote(config['host'], config['port'], config['user'], config['password'])

if args.challenge > -1:
    print(sender.callMethod('SetNextChallengeIndex', args.challenge))

print(sender.callMethod('NextChallenge'))
