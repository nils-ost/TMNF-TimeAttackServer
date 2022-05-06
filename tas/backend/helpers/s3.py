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
    if config['bucket_replays'] not in [bucket['Name'] for bucket in botoClient.list_buckets()['Buckets']]:
        botoClient.create_bucket(Bucket=config['bucket_replays'])


setup_storage()


def replay_get(name):
    global config
    global botoClient
    if not name.endswith('.Replay.Gbx'):
        name = name + '.Replay.Gbx'
    result = botoClient.get_object(Bucket=config['bucket_replays'], Key=name)
    return result['Body']


def replay_exists(name):
    global config
    global botoClient
    if not name.endswith('.Replay.Gbx'):
        name = name + '.Replay.Gbx'
    try:
        objects = botoClient.list_objects(Bucket=config['bucket_replays'], Prefix=name)
        objects = [k for k in [obj['Key'] for obj in objects.get('Contents', [])]]
        if name in objects:
            return True
        else:
            return False
    except Exception:
        return False


def replay_delete_all():
    global config
    botoResource = boto3.resource(
        's3',
        endpoint_url=f"http://{config['host']}:{config['port']}",
        aws_access_key_id=config['access_key'],
        aws_secret_access_key=config['access_secret']
    )
    botoResource.Bucket(config['bucket_replays']).objects.all().delete()
