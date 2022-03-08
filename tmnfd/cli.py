#!/usr/bin/python3

import os
import argparse
from helpers.config import get_config, save_config
from helpers.settings import DedicatedCfg, MatchSettings
os.chdir(os.path.dirname(os.path.realpath(__file__)))

parser = argparse.ArgumentParser(description="TMNFD CLI")
parser.add_argument('--init', dest='init', action='store_true', default=False, help='Initialize Configuration')
parser.add_argument('--force-init', dest='force_init', action='store_true', default=False, help='Initialize Configuration')
parser.add_argument('--write-active', dest='write_active', action='store_true', help='Write active MatchSettings')
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
