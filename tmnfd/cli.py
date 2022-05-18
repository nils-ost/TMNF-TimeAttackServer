import os
import sys
import argparse
from helpers.settings import DedicatedCfg, MatchSettings
from glob import glob
os.chdir(os.path.dirname(os.path.realpath(__file__)))

parser = argparse.ArgumentParser(description='TMNFD CLI')
parser.add_argument('--test', dest='test', action='store_true', default=False, help='Used for testing if tmnfd-cli is available')
parser.add_argument('--init', dest='init', action='store_true', default=False, help='Initialize Configuration')
parser.add_argument('--prepare-start', dest='prepare_start', action='store_true', help='Prepares everything for tmnfd to be started')
parser.add_argument('--upload_replay', dest='upload_replay', default=None, help='Uploads specified replay file to S3 storage')
parser.add_argument('--generate_thumbnails', dest='generate_thumbnails', action='store_true', help='Generates thumbnails and uploads them to S3 storage')
parser.add_argument('--upload_challenges', dest='upload_challenges', action='store_true', help='Uploads challenges files of active machsetting to S3 storage')
args = parser.parse_args()


def init_config(force=True):
    from helpers.config import get_config, save_config
    config = get_config()
    if force or not config.get('init', False):
        cfg = DedicatedCfg()
        cfg.set_name('TMNF-TAS')
        cfg.set_xmlrpc()
        cfg.set_laddermode()
        cfg.save()
        ms = MatchSettings(config['active_matchsetting'])
        ms.save(activate=True)
        config['init'] = True
        save_config(config)


def write_active():
    from helpers.config import get_config
    ms = MatchSettings(get_config()['active_matchsetting'])
    ms.save(activate=True)


def list_challenges():
    from pygbx import Gbx, GbxType
    from helpers.config import get_config
    path = get_config()['challenges_path']
    path += '' if path.endswith('/') else '/'
    for f in \
            glob(os.path.join(path, 'Campaigns', 'Nations', '**', '*.Challenge.Gbx'), recursive=True) + \
            glob(os.path.join(path, 'Challenges', '**', '*.Challenge.Gbx'), recursive=True):
        g = Gbx(f)
        challenge = g.get_class_by_id(GbxType.CHALLENGE)
        if not challenge:
            continue
        print(f"{challenge.map_name} {f.replace(path, '')} {challenge.map_uid}")


def generate_thumbnails(interactive=True):
    from helpers.config import get_config
    from helpers.thumbnails import extract_thumbnail
    from helpers.s3 import exists_thumbnail, upload_thumbnail
    config = get_config()
    ms = MatchSettings(config['active_matchsetting'])
    cpath = get_config()['challenges_path']
    for ident, path in ms.get_challenges():
        if not exists_thumbnail(ident):
            challenge_file = os.path.join(cpath, path.replace('\\', '/'))
            extract_thumbnail(challenge_file, '/tmp/thumbnail.jpg')
            upload_thumbnail('/tmp/thumbnail.jpg', ident)
            if interactive:
                print(f'Extracted thumbnail from {challenge_file}')
        elif interactive:
            print(f'Thumbnail {ident}.jpg exists')


def upload_challenges(interactive=True):
    from helpers.config import get_config
    from helpers.s3 import exists_challenge, upload_challenge
    config = get_config()
    ms = MatchSettings(config['active_matchsetting'])
    for ident, cpath in ms.get_challenges():
        cpath = os.path.join(config['challenges_path'], cpath.replace('\\', '/'))
        if not exists_challenge(ident):
            upload_challenge(cpath, ident)
            if interactive:
                print(f'Uploaded: {cpath}')
        elif interactive:
            print(f'Allready exists: {cpath}')


def exit():
    sys.exit(0)


def upload_replay(replay):
    from helpers.s3 import upload_replay as s3_upload_replay
    from helpers.config import get_config
    replay_path = os.path.join(get_config()['replays_path'], replay)
    if not replay_path.endswith('.Replay.Gbx'):
        replay_path = replay_path + '.Replay.Gbx'
    s3_upload_replay(replay_path, replay)


commands = [
    ('Force Config Init', init_config),
    ('Write Active MatchSettings', write_active),
    ('List Challenges', list_challenges),
    ('Generate Thumbnails', generate_thumbnails),
    ('Upload Challenges', upload_challenges),
    ('Exit', exit)
]

if args.test:
    sys.exit(0)

elif args.init:
    init_config(False)

elif args.prepare_start:
    write_active()

elif args.generate_thumbnails:
    generate_thumbnails(False)

elif args.upload_replay:
    upload_replay(args.upload_replay)

elif args.upload_challenges:
    upload_challenges(False)

else:
    while True:
        index = 0
        for display, func in commands:
            print(f'{index} {display}')
            index += 1

        selection = int(input('\nSelect: '))
        if selection not in range(0, len(commands)):
            print('Invalid input!')
            sys.exit(1)

        commands[selection][1]()
        print()
