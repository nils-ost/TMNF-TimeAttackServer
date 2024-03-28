import boto3
from botocore.exceptions import ConnectionClosedError
from elements import Config
import sys
import logging

logger = logging.getLogger(__name__)
config = Config.get('s3')['content']

botoClient = boto3.client(
    's3',
    endpoint_url=f"http://{config['host']}:{config['port']}",
    aws_access_key_id=config['access_key'],
    aws_secret_access_key=config['access_secret']
)


def is_connected():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global botoClient
    origCT = botoClient.meta.config.connect_timeout
    botoClient.meta.config.connect_timeout = 1
    origRetries = botoClient.meta.config.retries
    botoClient.meta.config.retries = {'max_attempts': 0}
    result = False
    for i in range(3):
        try:
            botoClient.list_buckets()
            result = True
            break
        except ConnectionClosedError:
            continue
        except Exception:
            break
    botoClient.meta.config.connect_timeout = origCT
    botoClient.meta.config.retries = origRetries
    return result


def setup_storage():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global botoClient
    buckets = [bucket['Name'] for bucket in botoClient.list_buckets()['Buckets']]
    for bucket in [v for k, v in config.items() if k.startswith('bucket_')]:
        if bucket not in buckets:
            botoClient.create_bucket(Bucket=bucket)


if is_connected():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    setup_storage()


def generic_list(bucket):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global botoClient
    result = list()
    for c in botoClient.list_objects(Bucket=bucket).get('Contents', list()):
        if c.get('Key'):
            result.append(c.get('Key'))
    return result


def generic_get(bucket, name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global botoClient
    result = botoClient.get_object(Bucket=bucket, Key=name)
    return result['Body']


def generic_exists(bucket, name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global botoClient
    try:
        objects = botoClient.list_objects(Bucket=bucket, Prefix=name)
        objects = [k for k in [obj['Key'] for obj in objects.get('Contents', [])]]
        if name in objects:
            return True
        else:
            return False
    except Exception:
        return False


def generic_delete_all(bucket):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    botoResource = boto3.resource(
        's3',
        endpoint_url=f"http://{config['host']}:{config['port']}",
        aws_access_key_id=config['access_key'],
        aws_secret_access_key=config['access_secret']
    )
    botoResource.Bucket(bucket).objects.all().delete()


def replay_get(name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if not name.endswith('.Replay.Gbx'):
        name = name + '.Replay.Gbx'
    return generic_get(config['bucket_replays'], name)


def replay_exists(name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if not name.endswith('.Replay.Gbx'):
        name = name + '.Replay.Gbx'
    return generic_exists(config['bucket_replays'], name)


def replay_delete_all():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    generic_delete_all(config['bucket_replays'])


def thumbnail_get(name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if not name.endswith('.jpg'):
        name = name + '.jpg'
    return generic_get(config['bucket_thumbnails'], name)


def thumbnail_exists(name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if not name.endswith('.jpg'):
        name = name + '.jpg'
    return generic_exists(config['bucket_thumbnails'], name)


def thumbnail_delete_all():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    generic_delete_all(config['bucket_thumbnails'])


def challenge_get(name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if not name.endswith('.Challenge.Gbx'):
        name = name + '.Challenge.Gbx'
    return generic_get(config['bucket_challenges'], name)


def challenge_exists(name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if not name.endswith('.Challenge.Gbx'):
        name = name + '.Challenge.Gbx'
    return generic_exists(config['bucket_challenges'], name)


def challenge_delete_all():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    generic_delete_all(config['bucket_challenges'])


def matchsetting_list():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    return generic_list(config['bucket_matchsettings'])


def matchsetting_get(name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if not name.endswith('.txt'):
        name = name + '.txt'
    return generic_get(config['bucket_matchsettings'], name)


def matchsetting_exists(name):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    if not name.endswith('.txt'):
        name = name + '.txt'
    return generic_exists(config['bucket_matchsettings'], name)


def buckets_delete_all():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global config
    for bucket in [v for k, v in config.items() if k.startswith('bucket_')]:
        generic_delete_all(bucket)
