import boto3
import os
from helpers.config import get_config

config = get_config().get('s3')

botoClient = boto3.client(
    's3',
    endpoint_url=f"http://{config['host']}:{config['port']}",
    aws_access_key_id=config['access_key'],
    aws_secret_access_key=config['access_secret']
)


def setup_storage():
    global botoClient
    buckets = [bucket['Name'] for bucket in botoClient.list_buckets()['Buckets']]
    for bucket in [config['bucket_replays'], config['bucket_thumbnails']]:
        if bucket not in buckets:
            botoClient.create_bucket(Bucket=bucket)


setup_storage()


def upload_generic(bucket, path, name):
    global botoClient
    if not os.path.isfile(path):
        return False
    try:
        with open(path, 'rb') as f:
            botoClient.upload_fileobj(f, Bucket=bucket, Key=name)
        os.remove(path)
        return True
    except Exception:
        return False


def upload_replay(path, name):
    global config
    if not name.endswith('.Replay.Gbx'):
        name = name + '.Replay.Gbx'
    return upload_generic(config['bucket_replays'], path, name)


def upload_thumbnail(path, name):
    global config
    if not name.endswith('.jpg'):
        name = name + '.jpg'
    return upload_generic(config['bucket_thumbnails'], path, name)


def exists_generic(bucket, name):
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


def exists_thumbnail(name):
    global config
    if not name.endswith('.jpg'):
        name = name + '.jpg'
    return exists_generic(config['bucket_thumbnails'], name)
