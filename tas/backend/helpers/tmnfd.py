"""
TrachMania Nations Forever - Dedicated Server
"""
from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.mongodb import laptime_add, challenge_get, challenge_add, challenge_update, challenge_deactivate_all, challenge_id_get, challenge_id_set, player_update, ranking_clear, ranking_rebuild, set_tmnfd_name
import time
import sys

config = get_config('tmnf-server')
challenge_config = get_config('challenges')

watcher_process = None


def calcTimeLimit(rel_time, lap_race, nb_laps):
    if lap_race and nb_laps < 1:
        new_time = challenge_config['least_time']
    elif lap_race and nb_laps > 1:
        new_time = (rel_time / nb_laps) * challenge_config['least_rounds']
    else:
        new_time = rel_time * challenge_config['least_rounds']
    return int(max(new_time, challenge_config['least_time']))


def prepareChallenges(sender):
    challenge_deactivate_all()
    starting_index = 0
    infos_returned = 10
    fetched_count = 0
    while True:
        for challenge in sender.callMethod('GetChallengeList', infos_returned, starting_index)[0]:
            challenge = sender.callMethod('GetChallengeInfo', challenge['FileName'])[0]
            rel_time = challenge.get(challenge_config['rel_time'], 30000)
            time_limit = calcTimeLimit(rel_time, challenge['LapRace'], challenge['NbLaps'])
            challenge_add(challenge['UId'], challenge['Name'], time_limit, rel_time, challenge['LapRace'])
            fetched_count += 1
        if fetched_count % infos_returned == 0:
            starting_index += infos_returned
        else:
            break
    ranking_clear()
    ranking_rebuild()


def prepareNextChallenge(sender):
    challenge = sender.callMethod('GetNextChallengeInfo')[0]
    time_limit = challenge_get(challenge['UId'])['time_limit']
    sender.callMethod('SetTimeAttackLimit', time_limit)
    challenge_id_set(challenge['UId'], next=True)
    print(f"Challenge next: {challenge['Name']} - AttackLimit: {int(time_limit / 1000)}s")


def worker_function(msg_queue, sender):
    while True:
        func, params = msg_queue.get()

        if func == 'TrackMania.PlayerFinish':
            current_challenge = challenge_id_get(current=True)
            if current_challenge is not None:
                player_id, player_login, player_time = params
                laptime_add(player_login, current_challenge, player_time)
                if player_time > 0:
                    print(f"{player_login} drove: {player_time / 1000}")

        elif func == 'TrackMania.BeginRace':
            challenge_db = challenge_get(params[0]['UId'])
            if challenge_db['lap_race'] and challenge_db['nb_laps'] == -1:
                new_time = calcTimeLimit(challenge_db['rel_time'], True, params[0]['NbLaps'])
                challenge_update(params[0]['UId'], time_limit=new_time, nb_laps=params[0]['NbLaps'])
            else:
                challenge_update(params[0]['UId'])
            challenge_id_set(params[0]['UId'], current=True)
            print(f"Challenge begin: {params[0]['Name']}")
            prepareNextChallenge(sender)

        elif func == 'TrackMania.EndRace':
            old_challenge = challenge_id_get(current=True)
            challenge_id_set(None, current=True)
            if old_challenge is not None:
                ranking_rebuild(old_challenge)
            print(f"Challenge end: {params[1]['Name']}")

        elif func == 'TrackMania.PlayerInfoChanged':
            player = params[0]
            player_update(player['Login'], player['NickName'], player['PlayerId'])

        elif func == 'TrackMania.PlayerConnect':
            print(f"{params[0]} connected")

        elif func == 'TrackMania.PlayerDisconnect':
            print(f"{params[0]} disconnected")


def receiver_function(msg_queue, receiver):
    while True:
        try:
            msg_queue.put(receiver.receiveCallback())
        except ConnectionResetError:
            print("Lost connection to: TMNF - Dedicated Server")
            return


def watcher_function():
    BaseManager.register('GbxRemote', GbxRemote)
    manager = BaseManager()
    manager.start()
    receiver = manager.GbxRemote(config['host'], config['port'], config['user'], config['password'])
    sender = manager.GbxRemote(config['host'], config['port'], config['user'], config['password'])

    callback_queue = Queue()
    worker_process = Process(target=worker_function, args=(callback_queue, sender, ), daemon=True)
    worker_process.start()
    receiver_process = Process(target=receiver_function, args=(callback_queue, receiver, ), daemon=True)

    first_start = True
    while True:
        if not receiver_process.is_alive():
            delay_counter = 0
            while not receiver.connect():
                if delay_counter == 0:
                    print("Waiting for: TMNF - Dedicated Server")
                delay_counter = (delay_counter + 1) % 30
                time.sleep(1)
            while not sender.connect():
                time.sleep(1)
            print("Connected to: TMNF - Dedicated Server")
            prepareChallenges(sender)

            server_name = sender.callMethod('GetServerName')[0]
            set_tmnfd_name(server_name)
            print(f"TMNF - Dedicated Server Name: {server_name}")
            current_challenge = sender.callMethod('GetCurrentChallengeInfo')[0]
            challenge_update(current_challenge['UId'], force_inc=False)
            print(f"Challenge current: {current_challenge['Name']}")
            challenge_id_set(current_challenge['UId'], current=True)
            prepareNextChallenge(sender)
            if first_start:
                first_start = False
            else:
                if sys.version_info.minor >= 7:
                    receiver_process.close()
                receiver_process = Process(target=receiver_function, args=(callback_queue, receiver, ), daemon=True)
            receiver_process.start()
        time.sleep(1)


def connect():
    global watcher_process

    if watcher_process is None:
        watcher_process = Process(target=watcher_function)
        watcher_process.start()
