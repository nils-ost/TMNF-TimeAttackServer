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
    if config['bucket_replays'] not in [bucket['Name'] for bucket in botoClient.list_buckets()['Buckets']]:
        botoClient.create_bucket(Bucket=config['bucket_replays'])


setup_storage()


def upload_replay(path, name):
    global botoClient
    global config
    if not name.endswith('.Replay.Gbx'):
        name = name + '.Replay.Gbx'
    if not os.path.isfile(path):
        return False
    try:
        with open(path, 'rb') as f:
            botoClient.upload_fileobj(f, Bucket=config['bucket_replays'], Key=name)
        os.remove(path)
        return True
    except Exception:
        return False
