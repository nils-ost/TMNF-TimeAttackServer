import os
import json


loaded = False
_config = {
    'config_path': '/cfg/dedicated_cfg.txt',
    'match_settings': '/cfg/MatchSettings',
    'active_path': '/cfg/active_ms.txt',
    'challenges_path': '/cfg/Tracks',
    'active_matchsetting': 'NationsWhite.txt',
    'replays_path': '/tmdedicated/GameData/Tracks/Replays',
    'hot_seat_mode': False,
    'saved_max_players': 32,
    's3': {
        'host': 'minio',
        'port': 9000,
        'access_key': 'tmnftas',
        'access_secret': 'password',
        'bucket_replays': 'tas-replays',
        'bucket_thumbnails': 'tas-thumbnails',
        'bucket_challenges': 'tas-challenges'
    }
}


def reload_config():
    global loaded
    loaded = False


def get_config():
    global loaded
    cfg_file = os.environ['TMNFD_CONFIG_FILE'] if 'TMNFD_CONFIG_FILE' in os.environ else 'config.json'
    if not loaded:
        loaded = True
        if os.path.isfile(cfg_file):
            with open(cfg_file, 'r') as f:
                _config.update(json.loads(f.read()))
        else:
            save_config(_config)
    return _config


def save_config(config):
    cfg_file = os.environ['TMNFD_CONFIG_FILE'] if 'TMNFD_CONFIG_FILE' in os.environ else 'config.json'
    _config = config
    with open(cfg_file, 'w') as f:
        f.write(json.dumps(_config, indent=4))
