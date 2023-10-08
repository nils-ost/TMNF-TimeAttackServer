"""
TrachMania Nations Forever - Dedicated Server Worker
"""
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.mongodb import laptime_add, challenge_get, challenge_update, challenge_id_get, challenge_id_set
from helpers.mongodb import player_update, player_get, ranking_rebuild, bestlaptime_get, clean_player_id
from helpers.mongodb import get_provide_replays, replay_add, get_start_time, get_end_time
from helpers.mongodb import hotseat_player_name_get, get_hotseat_mode, hotseat_player_ingameid_set, hotseat_player_ingameid_get
from helpers.tmnfdcli import tmnfd_cli_upload_replay
from helpers.rabbitmq import consume_dedicated_received_messages, send_dedicated_state_changes
import time
import hashlib

config = get_config('tmnf-server')
challenge_config = get_config('challenges')
sender = GbxRemote(config['host'], config['port'], config['user'], config['password'])


def isPreStart():
    startts = get_start_time()
    if startts is None:
        return False
    if time.time() < startts:
        return True
    return False


def isPostEnd():
    endts = get_end_time()
    if endts is None:
        return False
    if time.time() > endts:
        return True
    return False


def calcTimeLimit(rel_time, lap_race, nb_laps):
    if lap_race and nb_laps < 1:
        new_time = challenge_config['least_time']
    elif lap_race and nb_laps > 1:
        new_time = (rel_time / nb_laps) * challenge_config['least_rounds']
    else:
        new_time = rel_time * challenge_config['least_rounds']
    return int(max(new_time, challenge_config['least_time']))


def prepareNextChallenge(sender):
    challenge = sender.callMethod('GetNextChallengeInfo')[0]
    time_limit = challenge_get(challenge['UId'])['time_limit']
    sender.callMethod('SetTimeAttackLimit', time_limit)
    challenge_id_set(challenge['UId'], next=True)
    print(f"Challenge next: {challenge['Name']} - AttackLimit: {int(time_limit / 1000)}s")


def sendLaptimeNotice(sender, player_login, player_time=None):
    def timetos(time):
        if time is None:
            return '---'
        m = int(abs(time) / 10)
        ms = int(m % 100)
        m = int(m / 100)
        s = int(m % 60)
        m = int(m / 60)
        return f"{'-' if time < 0 else ''}{m}:{'0' if s < 10 else ''}{s}.{'0' if ms < 10 else ''}{ms}"
    player_id = clean_player_id(player_login)
    player = player_get(player_id=player_id)
    if player is None:
        return
    best = bestlaptime_get(player_id=player_id, challenge_id=challenge_id_get(current=True))
    msg = None
    if best is None:
        if get_hotseat_mode():
            msg = f'Hello {player_login}. Have fun on the HotSeat!'
        else:
            msg = "You don't have a PB on this Challenge yet"
    elif player_time is None:
        if get_hotseat_mode():
            msg = f"Welcome back {player_login}! Your PB is: {timetos(best['time'])}"
        else:
            msg = f"Your PB on this Challenge is: {timetos(best['time'])}"
    elif player_time == 0:
        pass
    elif player_time == best['time']:
        msg = f"You drove a PB with: {timetos(best['time'])}"
    elif best['time'] is not None:
        msg = f"You drove {timetos(player_time)} thats {timetos(player_time - best['time'])} behind your PB ({timetos(best['time'])})"
    if msg:
        if get_hotseat_mode():
            sender.callMethod('SendNoticeToId', hotseat_player_ingameid_get(), msg, 255, 20)
        else:
            sender.callMethod('SendNoticeToId', player['current_uid'], msg, 255, 20)


def worker_function(func, params, ch, delivery_tag):
    global sender
    print('Received:', func, params)

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
                print(f'{player_login} drove: {player_time / 1000}')
            sendLaptimeNotice(sender, player_login, player_time)
            player_update(player_login)  # keep track of last update, even if player never reaches finish
            if new_best and get_provide_replays():
                player_hash = hashlib.md5(player_login.encode('utf-8')).hexdigest()
                replay_name = f'{player_hash}_{ts}'
                if sender.callMethod('SaveBestGhostsReplay', player_login, replay_name)[0]:
                    if tmnfd_cli_upload_replay(replay_name):
                        replay_add(player_login, current_challenge, ts, replay_name)
                        print(f'Providing Replay: {replay_name}')
                    else:
                        print('Replay could not be provided!')
                else:
                    print('Replay could not be provided!')

    elif func == 'TrackMania.BeginRace':
        if isPreStart() or isPostEnd():
            if isPostEnd():
                challenge_id_set(params[0]['UId'], current=True)
                next_challenge = sender.callMethod('GetNextChallengeInfo')[0]
                challenge_id_set(next_challenge['UId'], next=True)
                print(f"Post End Challenge begin: {params[0]['Name']}")
            else:
                challenge_id_set(None, current=True)
                challenge_id_set(None, next=True)
                print(f"Pre Start Challenge begin: {params[0]['Name']}")
        else:
            challenge_db = challenge_get(params[0]['UId'])
            if challenge_db['lap_race'] and challenge_db['nb_laps'] == -1:
                new_time = calcTimeLimit(challenge_db['rel_time'], True, params[0]['NbLaps'])
                challenge_update(params[0]['UId'], time_limit=new_time, nb_laps=params[0]['NbLaps'])
            else:
                challenge_update(params[0]['UId'])
            challenge_id_set(params[0]['UId'], current=True)
            print(f"Challenge begin: {params[0]['Name']}")
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
            print(f"Challenge end: {params[1]['Name']}")

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
        print(f'{player_login} connected')
        player_update(player_login, connected=True, connect_msg_send=False)

    elif func == 'TrackMania.PlayerDisconnect':
        player_login = params[0]
        if get_hotseat_mode():
            player_login = hotseat_player_name_get()
            if player_login is None:
                ch.basic_ack(delivery_tag=delivery_tag)
                return
        print(f'{player_login} disconnected')
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
    consume_dedicated_received_messages(worker_function)
