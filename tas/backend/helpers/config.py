import os
import json


config = {
    'tmnf-server': {
        'host': 'localhost',
        'port': 5000,
        'user': 'SuperAdmin',
        'password': 'SuperAdmin'
    },
    'mongo': {
        'host': 'localhost',
        'port': 27017,
        'database': 'tmnf-tas'
    },
    'challenges': {
        'rel_time': 'SilverTime',
        'least_rounds': 6,
        'least_time': 300000
    },
    'server': {
        'port': 8000
    },
    'metrics': {
        'enabled': False,
        'port': 8001
    },
    's3': {
        'host': 'localhost',
        'port': 9000,
        'access_key': 'tmnftas',
        'access_secret': 'password',
        'bucket_replays': 'tas-replays',
        'bucket_thumbnails': 'tas-thumbnails',
        'bucket_challenges': 'tas-challenges'
    },
    'util': {
        'wallboard_players_max_default': 10,
        'wallboard_challenges_max_default': 8
    }
}

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config.update(json.loads(f.read()))
else:
    with open('config.json', 'w') as f:
        f.write(json.dumps(config, indent=4))


def get_config(portion=None):
    global config
    if portion is None:
        return config
    else:
        return config.get(portion, None)


def set_config(nconfig, portion=None):
    global config
    if portion is None:
        config = nconfig
    else:
        config[portion] = nconfig
    with open('config.json', 'w') as f:
        f.write(json.dumps(config, indent=4))
