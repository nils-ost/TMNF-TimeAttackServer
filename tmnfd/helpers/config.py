import os
import sys
import json
import logging

logger = logging.getLogger(__name__)
loaded = False
_config = {
    'config_path': '/cfg/dedicated_cfg.txt',
    'match_settings': '/tracks/MatchSettings',
    'active_path': '/cfg/active_ms.txt',
    'challenges_path': '/tracks',
    'active_matchsetting': 'NationsWhite.txt',
    'replays_path': '/tmdedicated/GameData/Tracks/Replays',
    'hot_seat_mode': False,
    'dedicated': {
        'ingame_name': 'TMNF-TAS',
        'max_players': 32,
        'game_port': 2350,
        'p2p_port': 3450,
        'rpc_port': 5000,
        'superadmin_pw': 'SuperAdmin',
        'admin_pw': 'Admin',
        'user_pw': 'User',
        'callvote_timeout': 0,
        'callvote_ratio': -1,
    },
    's3': {
        'host': 'minio',
        'port': 9000,
        'access_key': 'tmtas',
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
                for k, v in json.loads(f.read()).items():
                    if isinstance(v, dict) and k in _config:
                        for a, b in v.items():
                            _config[k][a] = b
                    else:
                        _config[k] = v
        else:
            save_config(_config)
    return _config


def save_config(config):
    cfg_file = os.environ['TMNFD_CONFIG_FILE'] if 'TMNFD_CONFIG_FILE' in os.environ else 'config.json'
    _config = config
    with open(cfg_file, 'w') as f:
        f.write(json.dumps(_config, indent=4))


def update_config_from_orchestrator():
    def _callback(timeout, config):
        if timeout:
            logger.critical('orchestrator did not respond to config request! exiting...')
            sys.exit(1)
        new_config = get_config()
        for k, v in config.items():
            if isinstance(v, dict) and k in new_config:
                for a, b in v.items():
                    new_config[k][a] = b
            else:
                new_config[k] = v
        save_config(new_config)

    from helpers.rabbitmq import ask_orchestrator_for_config
    logger.info('asking orchestrator for config')
    config = get_config()
    ask_orchestrator_for_config(
        callback_func=_callback,
        container_id=os.environ.get('HOSTNAME', None),
        dedicated_type='tmnf',
        current_config=config,
        timeout=20)
