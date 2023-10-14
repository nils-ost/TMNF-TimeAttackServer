import logging
import sys

logger = logging.getLogger(__name__)

config = {
    'tmnf-server': {
        'host': 'tmnfd',
        'port': 5000,
        'user': 'SuperAdmin',
        'password': 'SuperAdmin'
    },
    'challenges': {
        'rel_time': 'SilverTime',
        'least_rounds': 6,
        'least_time': 300000
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
    }
}


def get_config(portion):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    from helpers.mongodb import get_config as mget_config
    db_config = mget_config(portion)
    if db_config is None:
        if portion not in config:
            return dict()
        else:
            from helpers.mongodb import set_config as mset_config
            db_config = config[portion]
            mset_config(portion, db_config)
    return db_config


def set_config(nconfig, portion):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    from helpers.mongodb import set_config as mset_config
    mset_config(portion, nconfig)
