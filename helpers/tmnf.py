from multiprocessing import Process, Queue
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.mongodb import laptime_add, challenge_get, challenge_add, challenge_update, challenge_id_get, challenge_id_set, player_update, ranking_rebuild

config = get_config('tmnf-server')
challenge_config = get_config('challenges')

receiver = None
sender = None

callback_queue = Queue()
receiver_process = None
worker_process = None


def calcTimeLimit(rel_time, lap_race, nb_laps):
    if lap_race and nb_laps < 1:
        new_time = challenge_config['least_time']
    elif lap_race and nb_laps > 1:
        new_time = (rel_time / nb_laps) * challenge_config['least_rounds']
    else:
        new_time = rel_time * challenge_config['least_rounds']
    return int(max(new_time, challenge_config['least_time']))


def prepareChallenges():
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
    ranking_rebuild()


def prepareNextChallenge():
    challenge = sender.callMethod('GetNextChallengeInfo')[0]
    time_limit = challenge_get(challenge['UId'])['time_limit']
    sender.callMethod('SetTimeAttackLimit', time_limit)
    challenge_id_set(challenge['UId'], next=True)
    print(f"Challenge next: {challenge['Name']} - AttackLimit: {int(time_limit / 1000)}s")


def receiver_function(msg_queue):
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
            prepareNextChallenge()

        elif func == 'TrackMania.EndRace':
            ranking_rebuild(challenge_id_get(current=True))  # triggers a last cache-rebuild
            challenge_id_set(None, current=True)
            print(f"Challenge end: {params[1]['Name']}")

        elif func == 'TrackMania.PlayerInfoChanged':
            player = params[0]
            player_update(player['Login'], player['NickName'], player['PlayerId'])

        elif func == 'TrackMania.PlayerConnect':
            print(f"{params[0]} connected")

        elif func == 'TrackMania.PlayerDisconnect':
            print(f"{params[0]} disconnected")


def worker_function(msg_queue):
    global receiver
    while True:
        msg_queue.put(receiver.receiveCallback())


def start_processes():
    global worker_process
    global receiver_process
    global receiver
    global sender
    global config

    receiver = GbxRemote(config['host'], config['port'], config['user'], config['password'])
    sender = GbxRemote(config['host'], config['port'], config['user'], config['password'])
    prepareChallenges()

    current_challenge = sender.callMethod('GetCurrentChallengeInfo')[0]
    challenge_update(current_challenge['UId'], force_inc=False)
    print(f"Challenge current: {current_challenge['Name']}")
    challenge_id_set(current_challenge['UId'], current=True)
    prepareNextChallenge()

    if worker_process is None:
        worker_process = Process(target=worker_function, args=(callback_queue, ), daemon=True)
        worker_process.start()
    if receiver_process is None:
        receiver_process = Process(target=receiver_function, args=(callback_queue, ), daemon=True)
        receiver_process.start()
