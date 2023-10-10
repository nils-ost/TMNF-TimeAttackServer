import os
import json
import logging
import sys

logger = logging.getLogger(__name__)

config = {
    'tmnf-server': {
        'host': 'localhost',
        'port': 5000,
        'user': 'SuperAdmin',
        'password': 'SuperAdmin'
    },
    'mongo': {
        'host': 'mongodb',
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
        'host': 'minio',
        'port': 9000,
        'access_key': 'tmnftas',
        'access_secret': 'password',
        'bucket_replays': 'tas-replays',
        'bucket_thumbnails': 'tas-thumbnails',
        'bucket_challenges': 'tas-challenges'
    },
    'rabbit': {
        'host': 'rabbitmq',
        'port': 5672,
        'queue_dedicated_received_messages': 'ded_rx_msg',
        'queue_dedicated_state_changes': 'ded_st_chg'
    },
    'util': {
        'wallboard_players_max_default': 10,
        'wallboard_challenges_max_default': 8,
        'wallboard_tables_max_default': 3
    }
}


def reload_config():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    cfg_file = os.environ['TAS_CONFIG_FILE'] if 'TAS_CONFIG_FILE' in os.environ else 'config.json'
    if os.path.isfile(cfg_file):
        with open(cfg_file, 'r') as f:
            fconfig = json.load(f)
        for k in fconfig.keys():
            config[k].update(fconfig[k])
    else:
        try:
            with open(cfg_file, 'w') as f:
                f.write(json.dumps(config, indent=4))
        except Exception:
            logger.warning(f'Could not write: {cfg_file}')


def get_config(portion=None):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if portion is None:
        return config
    else:
        return config.get(portion, None)


def set_config(nconfig, portion=None):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    cfg_file = os.environ['TAS_CONFIG_FILE'] if 'TAS_CONFIG_FILE' in os.environ else 'config.json'
    if portion is None:
        config = nconfig
    else:
        config[portion] = nconfig
    try:
        with open(cfg_file, 'w') as f:
            f.write(json.dumps(config, indent=4))
    except Exception:
        logger.warning(f'Could not write: {cfg_file}')


reload_config()
