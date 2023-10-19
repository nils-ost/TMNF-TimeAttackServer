import os
import json
import sys
import pika
import subprocess
from datetime import datetime
from helpers.config import get_config, set_config
from helpers.rabbitmq import wait_for_connection as mq_wait_for_connection, send_orchestrator_message
from helpers.mongodb import challenge_id_get, player_update, player_all, ranking_rebuild, hotseat_player_name_set, get_hotseat_mode
import logging

logger = logging.getLogger(__name__)
periodic_counter = 0


def consume_orchestrator_messages(callback_func, timeout=1):
    """
    callback_func needs to take timeout, func, params, ch, props and delivery_tag as arguments
    """
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    mq_wait_for_connection()
    rabbit_config = get_config('rabbit')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_config['host'], port=rabbit_config['port']))
    channel = connection.channel()
    channel.queue_declare(queue=rabbit_config['queue_orchestrator'])
    try:
        for method, properties, body in channel.consume(
                queue=rabbit_config['queue_orchestrator'], auto_ack=False, exclusive=True, inactivity_timeout=timeout):
            if method is None and properties is None and body is None:
                callback_func(timeout=True, func=None, params=None, ch=channel, props=None, delivery_tag=None)
            else:
                func, params = json.loads(body.decode())
                callback_func(timeout=False, func=func, params=params, ch=channel, props=properties, delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f'{sys._getframe().f_code.co_name} {e} {repr(e)}')
    finally:
        channel.cancel()


def identify_dedicated_server(container_id, dtype):
    """
    trys to identify the corresponding key in dedicated config for a given containerid and dedicated-type
    """
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    container_id = container_id.lower()
    dcmd = 'docker' if int(subprocess.check_output('id -u', shell=True).decode('utf-8').strip()) == 0 else 'sudo docker'
    try:
        container_config = json.loads(subprocess.check_output(f'{dcmd} inspect {container_id}', shell=True).decode('utf-8'))
    except Exception:
        logger.warning(f"{sys._getframe().f_code.co_name} Couldn't identify container {container_id}")
        return None
    if len(container_config) == 0:
        logger.warning(f"{sys._getframe().f_code.co_name} Couldn't identify container {container_id}")
        return None
    container_config = container_config[0]
    if 'com.docker.compose.service' in container_config['Config'].get('Labels', dict()):
        # seems to be defined in compose using it's service-name as container-name
        container_name = container_config['Config']['Labels']['com.docker.compose.service']
    else:
        # not defined in compose using it's real container-name
        container_name = container_config['Name']
    for k, v in get_config('dedicated').items():
        if v.get('type') == dtype and v.get('container') == container_name:
            return k
    logger.warning(f"{sys._getframe().f_code.co_name} Couldn't identify container {container_id}. {container_name} - {dtype} combo not present in config")
    return None


def container_running(container_id):
    """
    returns if the container with the given container_id is running or not (stopped, exited, ...)
    """
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    if container_id is None:
        return False
    container_id = container_id.lower()
    dcmd = 'docker' if int(subprocess.check_output('id -u', shell=True).decode('utf-8').strip()) == 0 else 'sudo docker'
    try:
        o = subprocess.check_output(f"{dcmd} ps -a -f id={container_id} --format='\u007b\u007b.State\u007d\u007d'", shell=True).decode('utf-8').strip()
        logger.debug(f'{sys._getframe().f_code.co_name} {o}')
        return o.lower() == 'running'
    except Exception:
        return False


def periodic_events_function():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    # rebuild rankings
    current_challenge = challenge_id_get(current=True)
    if current_challenge is not None:
        ranking_rebuild(current_challenge)
    # check active players for hotseat-mode
    if get_hotseat_mode():
        ts = int(datetime.now().timestamp())
        one_playing = False
        for p in player_all():
            if p.get('connected'):
                if (ts - p.get('ts', ts)) > 60:
                    player_update(player_id=p.get('_id'), connected=False, ts=ts)
                else:
                    one_playing = True
        if not one_playing:
            hotseat_player_name_set(None)
    # do maintenance for all dynamic containers
    dedicated_run_maintenance()


def issue_container_stop(container_id=None):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    if container_id is None:
        return
    send_orchestrator_message('Container.stop', dict({'container_id': container_id}))
    logger.info(f'{sys._getframe().f_code.co_name} Issued request to stop container: {container_id}')


def issue_container_start(container_type):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    ctype = None
    if container_type == 'dreceiver_container':
        ctype = 'dedicated-receiver'
    elif container_type == 'dresponder_container':
        ctype = 'dedicated-responder'
    elif container_type == 'dcontroller_container':
        ctype = 'dedicated-controller'
    if ctype is not None:
        send_orchestrator_message('Container.start', dict({'type': ctype}))
        logger.info(f'{sys._getframe().f_code.co_name} Issued request to start a container of type: {ctype}')


def dedicated_run_maintenance():
    """
    checks the dedicated_run config and clears it up
    """
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    ded_run = get_config('dedicated_run')
    ded = get_config('dedicated')
    keys_remove = list()
    keys_add = list()
    for k, v in ded_run.items():
        # check for outdated config objects
        if k not in ded:
            for ck in ['ded_container', 'dreceiver_container', 'dresponder_container', 'dcontroller_container']:
                issue_container_stop(v.get(ck))
            keys_remove.append(k)
            continue
        # check for dead containers
        if not container_running(v.get('ded_container')):
            for ck in ['dreceiver_container', 'dresponder_container', 'dcontroller_container']:
                issue_container_stop(v.get(ck))
            keys_remove.append(k)
            keys_add.append(k)
            continue
        for ck in ['dreceiver_container', 'dresponder_container', 'dcontroller_container']:
            if not container_running(v.get(ck)):
                issue_container_start(ck)
    # remove outdated or renewable configs
    for k in keys_remove:
        ded_run.pop(k, None)
    # check for configs missing in dedicated_run
    for k in ded.keys():
        if k not in ded_run and k not in keys_add:
            keys_add.append(k)
    # add all missing configs to dedicated_run
    for k in keys_add:
        ded_run[k] = ded[k]
    set_config(ded_run, 'dedicated_run')


def get_available_ports(dkey, dtype, preferred_port=None, preferred_p2p=None, preferred_rpc=None):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    available_ports = list([2350, 2351, 2352, 2353, 2354, 2355, 2356, 2357, 2358, 2359])
    available_p2p = list([3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459])
    available_rpc = list([5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009])

    for k, v in get_config('dedicated_run').items():
        if k == dkey or not dtype == v.get('type'):
            continue
        if v.get('game_port') is not None:
            available_ports.remove(v.get('game_port'))
        if v.get('p2p_port') is not None:
            available_p2p.remove(v.get('p2p_port'))
        if v.get('rpc_port') is not None:
            available_rpc.remove(v.get('rpc_port'))

    if preferred_port is None or int(preferred_port) not in available_ports:
        preferred_port = sorted(available_ports)[0]
    if preferred_p2p is None or int(preferred_p2p) not in available_p2p:
        preferred_p2p = sorted(available_p2p)[0]
    if preferred_rpc is None or int(preferred_rpc) not in available_rpc:
        preferred_rpc = sorted(available_rpc)[0]

    return (int(preferred_port), int(preferred_p2p), int(preferred_rpc))


def get_password(preferred_pw=None):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    if preferred_pw is None or preferred_pw in ['SuperAdmin', 'Admin', 'User']:
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(10))
    return preferred_pw


def build_dedicated_config(dedicated_key, current_config):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    ded_run = get_config('dedicated_run')
    ded_cfg = ded_run[dedicated_key]
    config = dict({'dedicated': {}})
    config['s3'] = get_config('s3')
    config['hot_seat_mode'] = True if ded_cfg.get('hot_seat_mode') or current_config.get('hot_seat_mode') else False

    port = current_config['dedicated'].get('game_port') if ded_cfg.get('game_port') is None else ded_cfg.get('game_port')
    p2p = current_config['dedicated'].get('p2p_port') if ded_cfg.get('p2p_port') is None else ded_cfg.get('p2p_port')
    rpc = current_config['dedicated'].get('rpc_port') if ded_cfg.get('rpc_port') is None else ded_cfg.get('rpc_port')
    port, p2p, rpc = get_available_ports(dedicated_key, ded_cfg['type'], port, p2p, rpc)
    config['dedicated']['game_port'] = port
    config['dedicated']['p2p_port'] = p2p
    config['dedicated']['rpc_port'] = rpc

    superadmin_pw = get_password(current_config['dedicated'].get('superadmin_pw') if ded_cfg.get('superadmin_pw') is None else ded_cfg.get('superadmin_pw'))
    admin_pw = get_password(current_config['dedicated'].get('admin_pw') if ded_cfg.get('admin_pw') is None else ded_cfg.get('admin_pw'))
    user_pw = get_password(current_config['dedicated'].get('user_pw') if ded_cfg.get('user_pw') is None else ded_cfg.get('user_pw'))
    config['dedicated']['superadmin_pw'] = superadmin_pw
    config['dedicated']['admin_pw'] = admin_pw
    config['dedicated']['user_pw'] = user_pw

    max_players = current_config.get('max_players') if ded_cfg.get('max_players') is None else ded_cfg.get('max_players')
    config['dedicated']['max_players'] = 32 if max_players is None else max_players
    ingame_name = current_config.get('ingame_name') if ded_cfg.get('ingame_name') is None else ded_cfg.get('ingame_name')
    config['dedicated']['ingame_name'] = 'TM-TAS' if ingame_name is None else ingame_name
    callvote_timeout = current_config.get('callvote_timeout') if ded_cfg.get('callvote_timeout') is None else ded_cfg.get('callvote_timeout')
    config['dedicated']['callvote_timeout'] = 0 if callvote_timeout is None else callvote_timeout
    callvote_ratio = current_config.get('callvote_ratio') if ded_cfg.get('callvote_ratio') is None else ded_cfg.get('callvote_ratio')
    config['dedicated']['callvote_ratio'] = -1 if callvote_ratio is None else callvote_ratio

    ded_run[dedicated_key]['hot_seat_mode'] = config['hot_seat_mode']
    ded_run[dedicated_key].update(config['dedicated'])
    set_config(ded_run, 'dedicated_run')
    return config


def messages_callback(timeout, func, params, ch, props, delivery_tag):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    if timeout:
        global periodic_counter
        periodic_counter = (periodic_counter + 1) % 5
        if periodic_counter == 0:
            periodic_events_function()
        return
    if func == 'Dedicated.config_request':
        container_id = params['container_id'].lower()
        dedicated_key = identify_dedicated_server(container_id, params['dedicated_type'])
        if dedicated_key is None:
            logger.warning(f'{sys._getframe().f_code.co_name} dedicated_key not resolvable, ignoring request')
            ch.basic_ack(delivery_tag=delivery_tag)
            return
        logger.info(f'{sys._getframe().f_code.co_name} TM-Dedicated container ({container_id}) is requesting config for: {dedicated_key}')
        ded_run = get_config('dedicated_run')
        if not ded_run[dedicated_key].get('ded_container') == container_id and container_running(ded_run[dedicated_key].get('ded_container')):
            logger.warning(f'{sys._getframe().f_code.co_name} dedicated-config ({dedicated_key}) allready attached with running container, ignoring request')
            ch.basic_ack(delivery_tag=delivery_tag)
            return
        # The following three lines ensure the _run config of dedicated-config is clean, also all other dedicated-config are up-to-date
        ded_run[dedicated_key]['ded_container'] = None
        set_config(ded_run, 'dedicated_run')
        dedicated_run_maintenance()
        config = build_dedicated_config(dedicated_key, params['current_config'])
        # finally link the requesting container to the dedicated-run config
        ded_run = get_config('dedicated_run')
        ded_run[dedicated_key]['ded_container'] = container_id
        set_config(ded_run, 'dedicated_run')
        ch.basic_publish(exchange='', routing_key=props.reply_to, body=json.dumps(config))
        logger.debug(f'{sys._getframe().f_code.co_name} Transmitted following config to container {ded_run[dedicated_key]["ded_container"]}: {config}')
    elif func == 'Dcontainer.attach_request':
        container_id = params['container_id'].lower()
        container_type = params['container_type'].lower()
        ded_run = get_config('dedicated_run')
        for k, v in ded_run.items():
            if not container_running(v.get(container_type + '_contianer')):
                ded_run[k][container_type + '_container'] = container_id
                set_config(ded_run, 'dedicated_run')
                ch.basic_publish(exchange='', routing_key=props.reply_to, body=json.dumps(dict({'dedicated_config': k})))
                logger.info(f'{sys._getframe().f_code.co_name} attached container {container_id} of type {container_type} to config {k}')
                break
        else:
            logger.warning(f'{sys._getframe().f_code.co_name} no container of type {container_type} needed, ignoring request from {container_id}')
            ch.basic_ack(delivery_tag=delivery_tag)
            return
    elif func == 'Container.stop':
        container_id = params['container_id'].lower()
        dcmd = 'docker' if int(subprocess.check_output('id -u', shell=True).decode('utf-8').strip()) == 0 else 'sudo docker'
        subprocess.check_output(f'{dcmd} stop {container_id}', shell=True)
        logger.info(f'{sys._getframe().f_code.co_name} Stopped container: {container_id}')
    elif func == 'Container.start':
        dcmd = 'docker' if int(subprocess.check_output('id -u', shell=True).decode('utf-8').strip()) == 0 else 'sudo docker'
        current_count = 0
        for container_id in subprocess.check_output(f"{dcmd} ps -a --format='\u007b\u007b.ID\u007d\u007d'", shell=True).decode('utf-8').strip().split('\n'):
            container_id = container_id.lower()
            detail = json.loads(subprocess.check_output(f'{dcmd} inspect {container_id}', shell=True).decode('utf-8'))[0]
            if detail['Config'].get('Labels', dict()).get('com.docker.compose.service') == params['type']:
                current_count += 1
                if not detail['State']['Running']:
                    subprocess.check_output(f'{dcmd} start {container_id}', shell=True)
                    logger.info(f'{sys._getframe().f_code.co_name} Started container: {container_id} to get another {params["type"]}')
                    break
        else:
            my_id = os.environ.get('HOSTNAME', 'localhost').lower()
            try:
                detail = json.loads(subprocess.check_output(f'{dcmd} inspect {my_id}', shell=True).decode('utf-8'))
                project = detail[0]['Config'].get('Labels', dict()).get('com.docker.compose.project', '')
                ccmd = f'{dcmd} compose --project-name {project}'
            except Exception:
                ccmd = f'{dcmd} compose --project-directory ../..'
            subprocess.check_output(f'{ccmd} up -d --no-recreate --scale {params["type"]}={current_count + 1}', shell=True)
            logger.info(f'{sys._getframe().f_code.co_name} Scaled {params["type"]} up by one, to get another container')
    ch.basic_ack(delivery_tag=delivery_tag)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level='INFO')
    dedicated_run_maintenance()
    consume_orchestrator_messages(messages_callback, timeout=1)
