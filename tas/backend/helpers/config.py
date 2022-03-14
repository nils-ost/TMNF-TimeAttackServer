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
        'database': 'tmnf-ta'
    },
    'challenges': {
        'rel_time': 'SilverTime',
        'least_rounds': 6,
        'least_time': 300000
    },
    'server': {
        'port': 8000
    },
    'util': {
        'wallboard_players_max_default': 10
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
