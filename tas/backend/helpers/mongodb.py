from pymongo import MongoClient, ASCENDING, DESCENDING
from helpers.config import get_config
from datetime import datetime
import multiprocessing

_mongoDB = dict()
config = get_config('mongo')


def start_mongodb_connection():
    global _mongoDB
    mongoClient = MongoClient(host=config['host'], port=int(config['port']), serverSelectionTimeoutMS=500)
    _mongoDB[multiprocessing.current_process().name] = mongoClient.get_database(config['database'])


def mongoDB():
    global _mongoDB
    p = multiprocessing.current_process().name
    if p not in _mongoDB:
        start_mongodb_connection()
    return _mongoDB[p]


"""
TMNF-TimeAttack
"""


def clean_player_id(player_id):
    return player_id.rsplit(':', 1)[0]


def print_all():
    print('challenges:')
    for c in mongoDB().challenges.find({}):
        print(c)
    print('players:')
    for p in mongoDB().players.find({}):
        print(p)
    print('laptimes:')
    for l in mongoDB().laptimes.find({}):
        print(l)
    print('bestlaptimes:')
    for l in mongoDB().bestlaptimes.find({}):
        print(l)


def laptime_add(player_id, challenge_id, time):
    ts = int(datetime.now().timestamp())
    player_id = clean_player_id(player_id)
    lt = {'player_id': player_id, 'challenge_id': challenge_id, 'time': time, 'created_at': ts}
    if time > 0:
        mongoDB().laptimes.insert_one(lt)
        best = mongoDB().bestlaptimes.find_one({'player_id': player_id, 'challenge_id': challenge_id})
        if best is None:
            mongoDB().bestlaptimes.insert_one(lt)
        elif best['time'] is None or best['time'] > time:
            mongoDB().bestlaptimes.update_one({'_id': best['_id']}, {'$set': {'time': time, 'created_at': ts}})
    elif time == 0 and mongoDB().bestlaptimes.find_one({'player_id': player_id, 'challenge_id': challenge_id}) is None:
        lt['time'] = None
        mongoDB().bestlaptimes.insert_one(lt)
    mongoDB().players.update_one({'_id': player_id}, {'$set': {'last_update': ts}})


def laptime_filter(player_id=None, challenge_id=None):
    f = dict({'time': {'$ne': None}})
    if player_id is not None:
        f['player_id'] = player_id
    if challenge_id is not None:
        f['challenge_id'] = challenge_id
    return mongoDB().laptimes.find(f).sort('created_at', ASCENDING)


def player_update(player_id, nickname, current_uid):
    ts = int(datetime.now().timestamp())
    player_id = clean_player_id(player_id)
    player = mongoDB().players.find_one({'_id': player_id})
    if player is None:
        player_ip = None
        if '/' in player_id:
            _, player_ip = player_id.split('/', 1)
            if not len(player_ip.split('.')) == 4:
                player_ip = None
        mongoDB().players.insert_one({'_id': player_id, 'current_uid': current_uid, 'nickname': nickname, 'last_update': ts, 'ip': player_ip})
    else:
        mongoDB().players.update_one({'_id': player_id}, {'$set': {'nickname': nickname, 'current_uid': current_uid, 'last_update': ts}})


def player_update_ip(player_id, player_ip):
    player = mongoDB().players.find_one({'_id': player_id})
    if player is None:
        return 1  # invalid player
    if player.get('ip', None) is not None:
        return 2  # player does allready have an IP assigned
    player_w_ip = mongoDB().players.find_one({'ip': player_ip})
    if player_w_ip is not None:
        return 3  # IP allready assigned to different player
    mongoDB().players.update_one({'_id': player_id}, {'$set': {'ip': player_ip}})
    return 0  # OK


def player_all():
    return mongoDB().players.find({})


def player_get(player_id=None, player_ip=None):
    if player_id is not None:
        return mongoDB().players.find_one({'_id': player_id})
    if player_ip is not None:
        return mongoDB().players.find_one({'ip': player_ip})
    return None


def challenge_add(challenge_id, name, time_limit, rel_time, lap_race):
    challenge = mongoDB().challenges.find_one({'_id': challenge_id})
    if challenge is None:
        mongoDB().challenges.insert_one({'_id': challenge_id, 'name': name, 'seen_count': 0, 'seen_last': None, 'time_limit': time_limit, 'rel_time': rel_time, 'lap_race': lap_race, 'nb_laps': -1, 'active': True})
    else:
        mongoDB().challenges.update_one({'_id': challenge_id}, {'$set': {'name': name, 'time_limit': time_limit, 'rel_time': rel_time, 'lap_race': lap_race, 'nb_laps': -1, 'active': True}})


def challenge_update(challenge_id, force_inc=True, time_limit=None, nb_laps=None):
    updates = dict({'$set': dict()})
    if time_limit is not None:
        updates['$set']['time_limit'] = time_limit
    if nb_laps is not None:
        updates['$set']['nb_laps'] = nb_laps
    if force_inc:
        updates['$set']['seen_last'] = int(datetime.now().timestamp())
        updates['$inc'] = {'seen_count': 1}
        mongoDB().challenges.update_one({'_id': challenge_id}, updates)
    else:
        updates['$set']['seen_last'] = {'$cond': [{'$eq': ['$seen_last', None]}, int(datetime.now().timestamp()), '$seen_last']}
        updates['$set']['seen_count'] = {'$cond': [{'$eq': ['$seen_count', 0]}, 1, '$seen_count']}
        mongoDB().challenges.update_one({'_id': challenge_id}, [updates])


def challenge_all():
    return mongoDB().challenges.find({'active': True})


def challenge_get(challenge_id=None, current=False, next=False):
    if current:
        challenge_id = challenge_id_get(current=True)
    if next:
        challenge_id = challenge_id_get(next=True)
    return mongoDB().challenges.find_one({'_id': challenge_id})


def challenge_deactivate_all():
    mongoDB().challenges.update_many({}, {'$set': {'active': False}})


def challenge_id_get(current=False, next=False):
    cid = None
    if current:
        cid = mongoDB().utils.find_one({'_id': 'current_challenge_id'})
    else:
        cid = mongoDB().utils.find_one({'_id': 'next_challenge_id'})
    if cid is None:
        return 'unknown'
    return cid['value']


def challenge_id_set(challenge_id, current=False, next=False):
    if current:
        mongoDB().utils.replace_one({'_id': 'current_challenge_id'}, {'_id': 'current_challenge_id', 'value': challenge_id}, True)
    else:
        mongoDB().utils.replace_one({'_id': 'next_challenge_id'}, {'_id': 'next_challenge_id', 'value': challenge_id}, True)


def ranking_player(player_id):
    result = list()
    for rp in mongoDB().rankings.find({'player_id': player_id}):
        rp.pop('_id')
        rp.pop('player_id')
        result.append(rp)
    return result


def ranking_for(challenge_id, current_challenge_id=None):
    if challenge_id == current_challenge_id:
        players = dict()
        players_none = list()
        for lt in mongoDB().bestlaptimes.find({'challenge_id': challenge_id, 'time': None}):
            players[lt['player_id']] = {'time': lt['time'], 'at': lt['created_at']}
            players_none.append(lt['player_id'])
        rank = 0
        step = 1
        time = None
        for lt in mongoDB().bestlaptimes.find({'challenge_id': challenge_id, 'time': {'$ne': None}}).sort('time', ASCENDING):
            p = lt['player_id']
            players[p] = {'time': lt['time'], 'at': lt['created_at']}
            if lt['time'] == time:
                step += 1
            else:
                rank += step
                step = 1
                time = lt['time']
            players[p]['rank'] = rank
        for p in players_none:
            players[p]['rank'] = len(players)
            players[p]['points'] = 0
        result = list()
        for p in players:
            if p not in players_none:
                players[p]['points'] = len(players) - (players[p]['rank'] - 1)
            rc = players[p]
            rc['player_id'] = p
            result.append(dict(rc))
            rc['challenge_id'] = challenge_id
            mongoDB().rankings.replace_one({'challenge_id': challenge_id, 'player_id': p}, rc, True)
        return result
    else:
        result = list()
        for rc in mongoDB().rankings.find({'challenge_id': challenge_id}).sort('rank', ASCENDING):
            rc.pop('_id')
            rc.pop('challenge_id')
            result.append(rc)
        return result


def ranking_global(current_challenge_id=None):
    if current_challenge_id is not None:
        ranking_for(current_challenge_id, current_challenge_id)  # forces ranking for current challenge to be rebuild
    result = list()
    rank = 0
    step = 1
    points = None
    for player in mongoDB().rankings.aggregate([{"$group": {'_id': '$player_id', 'points': {'$sum': '$points'}}}, {'$sort': {'points': DESCENDING}}]):
        if player['points'] == points:
            step += 1
        else:
            rank += step
            step = 1
            points = player['points']
        result.append({'player_id': player['_id'], 'rank': rank, 'points': points})
    return result


def ranking_rebuild(challenge_id=None):
    """
    Clears out ranking cache and rebuilds it for all challenges (or a singel challenge)
    """
    if challenge_id is not None:
        ranking_for(challenge_id, challenge_id)
    else:
        mongoDB().rankings.drop()
        for challenge in challenge_all():
            ranking_for(challenge['_id'], challenge['_id'])


"""
Settings
"""


def set_wallboard_players_max(c):
    mongoDB().utils.replace_one({'_id': 'wallboard_players_max'}, {'_id': 'wallboard_players_max', 'count': int(c)}, True)


def get_wallboard_players_max():
    r = mongoDB().utils.find_one({'_id': 'wallboard_players_max'})
    if r is None:
        wpmd = get_config('util')['wallboard_players_max_default']
        set_wallboard_players_max(wpmd)
        return wpmd
    else:
        return r['count']


def set_tmnfd_name(name):
    mongoDB().utils.replace_one({'_id': 'tmnfd_name'}, {'_id': 'tmnfd_name', 'name': name}, True)


def get_tmnfd_name():
    r = mongoDB().utils.find_one({'_id': 'tmnfd_name'})
    if r is None:
        return '--unknown--'
    return r.get('name', '--unknown--')


"""
Stats
"""


def get_players_count():
    ts = int(datetime.now().timestamp())
    r = mongoDB().utils.find_one({'_id': 'players_count'})
    if r is None or ts - r.get('ts', 0) > 10:
        count = mongoDB().players.count_documents({})
        mongoDB().utils.replace_one({'_id': 'players_count'}, {'_id': 'players_count', 'ts': ts, 'count': count}, True)
        return count
    else:
        return r.get('count', 0)


def get_active_players_count():
    ts = int(datetime.now().timestamp())
    r = mongoDB().utils.find_one({'_id': 'active_players_count'})
    if r is None or ts - r.get('ts', 0) > 10:
        count = mongoDB().players.count_documents({'last_update': {'$gt': ts - 61}})
        mongoDB().utils.replace_one({'_id': 'active_players_count'}, {'_id': 'active_players_count', 'ts': ts, 'count': count}, True)
        return count
    else:
        return r.get('count', 0)


def get_laptimes_count():
    ts = int(datetime.now().timestamp())
    r = mongoDB().utils.find_one({'_id': 'laptimes_count'})
    if r is None or ts - r.get('ts', 0) > 10:
        count = mongoDB().laptimes.count_documents({})
        mongoDB().utils.replace_one({'_id': 'laptimes_count'}, {'_id': 'laptimes_count', 'ts': ts, 'count': count}, True)
        return count
    else:
        return r.get('count', 0)


def get_laptimes_sum():
    ts = int(datetime.now().timestamp())
    r = mongoDB().utils.find_one({'_id': 'laptimes_sum'})
    if r is None or ts - r.get('ts', 0) > 10:
        s = mongoDB().laptimes.aggregate([{"$group": {'_id': 'sum', 'time': {'$sum': '$time'}}}]).next()['time']
        mongoDB().utils.replace_one({'_id': 'laptimes_sum'}, {'_id': 'laptimes_sum', 'ts': ts, 'sum': s}, True)
        return s
    else:
        return r.get('sum', 0)


def get_total_seen_count():
    ts = int(datetime.now().timestamp())
    r = mongoDB().utils.find_one({'_id': 'total_seen_count'})
    if r is None or ts - r.get('ts', 0) > 10:
        count = mongoDB().challenges.aggregate([{"$group": {'_id': 'sum', 'seen_count': {'$sum': '$seen_count'}}}]).next()['seen_count']
        mongoDB().utils.replace_one({'_id': 'total_seen_count'}, {'_id': 'total_seen_count', 'ts': ts, 'count': count}, True)
        return count
    else:
        return r.get('count', 0)
