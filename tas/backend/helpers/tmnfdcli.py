from helpers.mongodb import set_tmnfd_cli_method, get_tmnfd_cli_method, set_provide_replays
from elements import Config
import subprocess
import logging

logger = logging.getLogger(__name__)
config = Config.get('tmnf-server')['content']


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
        logger.warning('TMNF - Dedicated CLI is not reachable!')
        set_provide_replays(False)
        logger.info('  Disableing replay-provider')
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


def tmnfd_cli_create_backup():
    global config
    cli_method = get_tmnfd_cli_method()
    if cli_method == 'bash':
        result = subprocess.check_output('tmnfd --create_backup', shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
    if cli_method == 'ssh':
        result = subprocess.check_output(f"ssh root@{config['host']} tmnfd --create_backup", shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
    if result and 'uploaded' in result:
        return result.strip().split()[-1]
    return None


def tmnfd_cli_restore_backup():
    global config
    cli_method = get_tmnfd_cli_method()
    if cli_method == 'bash':
        return int(subprocess.call('tmnfd --restore_backup', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    if cli_method == 'ssh':
        return int(subprocess.call(
            f"ssh root@{config['host']} tmnfd --restore_backup", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    return False


def tmnfd_cli_hotseat_mode(enable=False):
    global config
    action = 'enable' if enable else 'disable'
    cli_method = get_tmnfd_cli_method()
    if cli_method == 'bash':
        return int(subprocess.call(f'tmnfd --{action}_hsm', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    if cli_method == 'ssh':
        return int(subprocess.call(
            f"ssh root@{config['host']} tmnfd --{action}_hsm", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)) == 0
    return False
