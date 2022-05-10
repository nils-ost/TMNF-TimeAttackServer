import boto3
from helpers.config import get_config

config = get_config('s3')

botoClient = boto3.client(
    's3',
    endpoint_url=f"http://{config['host']}:{config['port']}",
    aws_access_key_id=config['access_key'],
    aws_secret_access_key=config['access_secret']
)


def setup_storage():
    global botoClient
    buckets = [bucket['Name'] for bucket in botoClient.list_buckets()['Buckets']]
    for bucket in [v for k, v in config.items() if k.startswith('bucket_')]:
        if bucket not in buckets:
            botoClient.create_bucket(Bucket=bucket)


setup_storage()


def generic_get(bucket, name):
    global botoClient
    result = botoClient.get_object(Bucket=bucket, Key=name)
    return result['Body']


def generic_exists(bucket, name):
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
    botoResource = boto3.resource(
        's3',
        endpoint_url=f"http://{config['host']}:{config['port']}",
        aws_access_key_id=config['access_key'],
        aws_secret_access_key=config['access_secret']
    )
    botoResource.Bucket(bucket).objects.all().delete()


def replay_get(name):
    global config
    if not name.endswith('.Replay.Gbx'):
        name = name + '.Replay.Gbx'
    return generic_get(config['bucket_replays'], name)


def replay_exists(name):
    global config
    if not name.endswith('.Replay.Gbx'):
        name = name + '.Replay.Gbx'
    return generic_exists(config['bucket_replays'], name)


def replay_delete_all():
    global config
    generic_delete_all(config['bucket_replays'])


def thumbnail_get(name):
    global config
    if not name.endswith('.jpg'):
        name = name + '.jpg'
    return generic_get(config['bucket_thumbnails'], name)


def thumbnail_exists(name):
    global config
    if not name.endswith('.jpg'):
        name = name + '.jpg'
    return generic_exists(config['bucket_thumbnails'], name)


def thumbnail_delete_all():
    global config
    generic_delete_all(config['bucket_thumbnails'])


def buckets_delete_all():
    global config
    for bucket in [v for k, v in config.items() if k.startswith('bucket_')]:
        generic_delete_all(bucket)
