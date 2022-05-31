from helpers.mongodb import set_tmnfd_cli_method, get_tmnfd_cli_method, set_provide_replays
from helpers.config import get_config
import subprocess

config = get_config('tmnf-server')


def tmnfd_cli_test_method():
    global config
    r = subprocess.call('tmnfd --test', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if int(r) == 0:
        return 'bash'
    r = subprocess.call(f"ssh -o ConnectTimeout=3 root@{config['host']} tmnfd --test", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if int(r) == 0:
        return 'ssh'
    return None


def tmnfd_cli_test():
    method = tmnfd_cli_test_method()
    if method is None:
        print('TMNF - Dedicated CLI is not reachable!')
        set_provide_replays(False)
        print('  Disableing replay-provider')
    set_tmnfd_cli_method(method)
    return method


def tmnfd_cli_upload_replay(name):
    global config
    cli_method = get_tmnfd_cli_method()
    if cli_method == 'bash':
        return int(subprocess.call(f'tmnfd --upload_replay {name}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    if cli_method == 'ssh':
        return int(subprocess.call(
            f"ssh root@{config['host']} tmnfd --upload_replay {name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    return False


def tmnfd_cli_generate_thumbnails():
    global config
    cli_method = get_tmnfd_cli_method()
    if cli_method == 'bash':
        return int(subprocess.call('tmnfd --generate_thumbnails', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    if cli_method == 'ssh':
        return int(subprocess.call(
            f"ssh root@{config['host']} tmnfd --generate_thumbnails", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    return False


def tmnfd_cli_upload_challenges():
    global config
    cli_method = get_tmnfd_cli_method()
    if cli_method == 'bash':
        return int(subprocess.call('tmnfd --upload_challenges', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    if cli_method == 'ssh':
        return int(subprocess.call(
            f"ssh root@{config['host']} tmnfd --upload_challenges", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    return False
