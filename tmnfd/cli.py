import os
import argparse
from helpers.config import get_config, save_config
from helpers.settings import DedicatedCfg, MatchSettings
from glob import glob
from pygbx import Gbx, GbxType
os.chdir(os.path.dirname(os.path.realpath(__file__)))

parser = argparse.ArgumentParser(description="TMNFD CLI")
parser.add_argument('--init', dest='init', action='store_true', default=False, help='Initialize Configuration')
parser.add_argument('--force-init', dest='force_init', action='store_true', default=False, help='Initialize Configuration')
parser.add_argument('--write-active', dest='write_active', action='store_true', help='Write active MatchSettings')
parser.add_argument('--list-challenges', dest='list_challenges', action='store_true', help='Lists all available Challenges')
args = parser.parse_args()

if args.init or args.force_init:
    config = get_config()
    if args.force_init or not config.get('init', False):
        cfg = DedicatedCfg()
        cfg.set_name('TMNF-TAS')
        cfg.set_xmlrpc()
        cfg.set_laddermode()
        cfg.save()
        ms = MatchSettings(config['active_matchsetting'])
        ms.save(activate=True)
        config['init'] = True
        save_config(config)

if args.write_active:
    ms = MatchSettings(get_config()['active_matchsetting'])
    ms.save(activate=True)

if args.list_challenges:
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

"""Get Challenge Metadata

from pygbx import Gbx, GbxType

g = Gbx('A01-Race.Challenge.Gbx')
challenge = g.get_class_by_id(GbxType.CHALLENGE)
if not challenge:
    quit()

print(f'Map Name: {challenge.map_name}')
print(f'Map Author: {challenge.map_author}')
print(f'Environment: {challenge.environment}')
print(f'UUID: {challenge.map_uid}')

"""
