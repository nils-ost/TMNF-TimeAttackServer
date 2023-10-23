"""
TrachMania Nations Forever - Dedicated Server Responder
"""
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.mongodb import laptime_add, challenge_get, challenge_update, challenge_id_get, challenge_id_set
from helpers.mongodb import player_update, player_get, ranking_rebuild, clean_player_id, get_provide_replays, replay_add
from helpers.mongodb import hotseat_player_name_get, get_hotseat_mode, hotseat_player_ingameid_set
from helpers.tmnfd import isPreStart, isPostEnd, calcTimeLimit, prepareNextChallenge, sendLaptimeNotice
from helpers.tmnfdcli import tmnfd_cli_upload_replay
from helpers.rabbitmq import consume_dedicated_received_messages, send_dedicated_state_changes, request_attachement_from_orchestrator
import time
import hashlib
import logging

logger = logging.getLogger(__name__)
sender = None


def responder_function(func, params, ch, delivery_tag):
    global sender
    logger.info(f'Received: {func} {params}')

    if func == 'TrackMania.PlayerFinish':
        current_challenge = challenge_id_get(current=True)
        if current_challenge is not None:
            player_id, player_login, player_time = params
            if get_hotseat_mode():
                player_login = hotseat_player_name_get()
                if player_login is None:
                    ch.basic_ack(delivery_tag=delivery_tag)
                    return
                player_db = player_get(clean_player_id(player_login))
                if player_db is not None and not player_db['connect_msg_send']:
                    sendLaptimeNotice(sender, player_login)
                    player_update(player_login, connect_msg_send=True)
            ts, new_best = laptime_add(player_login, current_challenge, player_time)
            if player_time > 0:
                logger.info(f'{player_login} drove: {player_time / 1000}')
            sendLaptimeNotice(sender, player_login, player_time)
            player_update(player_login)  # keep track of last update, even if player never reaches finish
            if new_best and get_provide_replays():
                player_hash = hashlib.md5(player_login.encode('utf-8')).hexdigest()
                replay_name = f'{player_hash}_{ts}'
                if sender.callMethod('SaveBestGhostsReplay', player_login, replay_name)[0]:
                    if tmnfd_cli_upload_replay(replay_name):
                        replay_add(player_login, current_challenge, ts, replay_name)
                        logger.info(f'Providing Replay: {replay_name}')
                    else:
                        logger.warning('Replay could not be provided!')
                else:
                    logger.warning('Replay could not be provided!')

    elif func == 'TrackMania.BeginRace':
        if isPreStart() or isPostEnd():
            if isPostEnd():
                challenge_id_set(params[0]['UId'], current=True)
                next_challenge = sender.callMethod('GetNextChallengeInfo')[0]
                challenge_id_set(next_challenge['UId'], next=True)
                logger.info(f"Post End Challenge begin: {params[0]['Name']}")
            else:
                challenge_id_set(None, current=True)
                challenge_id_set(None, next=True)
                logger.info(f"Pre Start Challenge begin: {params[0]['Name']}")
        else:
            challenge_db = challenge_get(params[0]['UId'])
            if challenge_db['lap_race'] and challenge_db['nb_laps'] == -1:
                new_time = calcTimeLimit(challenge_db['rel_time'], True, params[0]['NbLaps'])
                challenge_update(params[0]['UId'], time_limit=new_time, nb_laps=params[0]['NbLaps'])
            else:
                challenge_update(params[0]['UId'])
            challenge_id_set(params[0]['UId'], current=True)
            logger.info(f"Challenge begin: {params[0]['Name']}")
            prepareNextChallenge(sender)
            if not get_hotseat_mode():
                for p in sender.callMethod('GetPlayerList', 0, 0)[0]:
                    sendLaptimeNotice(sender, p['Login'])

    elif func == 'TrackMania.EndRace':
        if not isPreStart() and not isPostEnd():
            old_challenge = challenge_id_get(current=True)
            challenge_id_set(None, current=True)
            if old_challenge is not None:
                ranking_rebuild(old_challenge)
            logger.info(f"Challenge end: {params[1]['Name']}")

    elif func == 'TrackMania.PlayerCheckpoint':
        if get_hotseat_mode():
            player_login = hotseat_player_name_get()
            if player_login is not None:
                player_db = player_get(clean_player_id(player_login))
                if player_db is not None and not player_db['connect_msg_send']:
                    sendLaptimeNotice(sender, player_login)
                    player_update(player_login, connect_msg_send=True)
                else:
                    player_update(player_login)  # keep track of last update, even if player never reaches finish
        else:
            player_update(params[1])  # keep track of last update, even if player never reaches finish

    elif func == 'TrackMania.PlayerInfoChanged':
        player = params[0]
        if get_hotseat_mode():
            hotseat_player_ingameid_set(player['PlayerId'])
            player['Login'] = hotseat_player_name_get()
            player['NickName'] = player['Login']
            if player['Login'] is None:
                ch.basic_ack(delivery_tag=delivery_tag)
                return
        player_update(player['Login'], player['NickName'], player['PlayerId'])
        player_db = player_get(clean_player_id(player['Login']))
        if player_db is not None and not player_db['connect_msg_send']:
            sendLaptimeNotice(sender, player['Login'])
            player_update(player['Login'], connect_msg_send=True)

    elif func == 'TrackMania.PlayerConnect':
        player_login = params[0]
        if get_hotseat_mode():
            player_login = hotseat_player_name_get()
            if player_login is None:
                ch.basic_ack(delivery_tag=delivery_tag)
                return
        logger.info(f'{player_login} connected')
        player_update(player_login, connected=True, connect_msg_send=False)

    elif func == 'TrackMania.PlayerDisconnect':
        player_login = params[0]
        if get_hotseat_mode():
            player_login = hotseat_player_name_get()
            if player_login is None:
                ch.basic_ack(delivery_tag=delivery_tag)
                return
        logger.info(f'{player_login} disconnected')
        player_update(player_login, connected=False)

    elif func == 'Dedicated.Disconnected':
        send_dedicated_state_changes('disconnected')
        challenge_id_set(None, current=True)
        challenge_id_set(None, next=True)

    elif func == 'Dedicated.Connected':
        send_dedicated_state_changes('connected')
        while not sender.connect():
            time.sleep(1)

    ch.basic_ack(delivery_tag=delivery_tag)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level='INFO')
    attached_config = request_attachement_from_orchestrator('dresponder')
    config = get_config('dedicated_run')[attached_config]
    sender = GbxRemote('host.docker.internal', config['rpc_port'], 'SuperAdmin', config['superadmin_pw'])
    consume_dedicated_received_messages(responder_function)
