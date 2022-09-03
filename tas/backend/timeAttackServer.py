import cherrypy
import cherrypy_cors
import time
import os
import json
from multiprocessing import Process
from urllib.parse import unquote
from cherrypy.lib import file_generator
from datetime import datetime
from helpers.mongodb import wait_for_mongodb_server, challenge_all, challenge_get, challenge_id_get
from helpers.mongodb import player_all, player_get, player_update_ip, laptime_filter, laptime_get
from helpers.mongodb import ranking_global, ranking_challenge, ranking_player, ranking_rebuild
from helpers.mongodb import get_wallboard_players_max, get_wallboard_challenges_max, get_tmnfd_name
from helpers.mongodb import get_display_self_url, get_display_admin, get_client_download_url
from helpers.mongodb import get_provide_replays, get_provide_thumbnails, get_provide_challenges, get_start_time, get_end_time
from helpers.mongodb import get_players_count, get_active_players_count, get_laptimes_count, get_laptimes_sum, get_total_seen_count
from helpers.tmnfd import connect as start_tmnfd_connection
from helpers.s3 import replay_get, replay_exists, thumbnail_get, thumbnail_exists, challenge_exists as challenge_exists_s3, challenge_get as challenge_get_s3
from helpers.config import get_config
from helpers.metrics import start_metrics_exporter


class TimeAttackServer():
    def __init__(self):
        self.challenges = Challenges()
        self.players = Players()
        self.rankings = Rankings()
        self.replays = Replays()
        self.thumbnails = Thumbnails()
        self.settings = Settings()
        self.stats = Stats()


class Settings():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        result = dict()
        result['wallboard_players_max'] = get_wallboard_players_max()
        result['wallboard_challenges_max'] = get_wallboard_challenges_max()
        result['tmnfd_name'] = get_tmnfd_name()
        result['display_self_url'] = get_display_self_url()
        result['display_admin'] = get_display_admin()
        result['client_download_url'] = get_client_download_url()
        result['provide_replays'] = get_provide_replays()
        result['provide_thumbnails'] = get_provide_thumbnails()
        result['provide_challenges'] = get_provide_challenges()
        result['start_time'] = get_start_time()
        result['end_time'] = get_end_time()
        cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=59'
        return result


class Stats():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        result = dict()
        result['total_players'] = get_players_count()
        result['active_players'] = get_active_players_count()
        result['laptimes_count'] = get_laptimes_count()
        result['laptimes_sum'] = get_laptimes_sum()
        result['challenges_total_seen_count'] = get_total_seen_count()
        cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=29'
        return result


@cherrypy.popargs('challenge_id')
class Challenges():
    @cherrypy.expose()
    def index(self, challenge_id=None):
        if challenge_id is None:
            result = list()
            for c in challenge_all():
                result.append({'id': c['_id'], 'name': c['name'], 'seen_count': c['seen_count'], 'seen_last': c['seen_last'], 'time_limit': c['time_limit']})
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=90'
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return json.dumps(result).encode('utf-8')

        challenge = challenge_get(challenge_id=challenge_id)
        if challenge is None or not challenge_exists_s3(challenge_id):
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=30'
            cherrypy.response.status = 404
            return
        else:
            filename = f"{challenge['name']}.Challenge.Gbx"
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=10000'
            cherrypy.response.headers['Content-Type'] = 'application/octet-stream'
            cherrypy.response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return file_generator(challenge_get_s3(challenge_id))

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def current(self):
        c = challenge_get(current=True)
        if c is None:
            return None
        c['id'] = c['_id']
        c.pop('_id', None)
        cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=9'
        return c

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def next(self):
        c = challenge_get(next=True)
        if c is None:
            return None
        c['id'] = c['_id']
        c.pop('_id', None)
        cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=9'
        return c


@cherrypy.popargs('player_id', 'details', 'challenge_id')
class Players():
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self, player_id=None, details=None, challenge_id=None):
        if not player_id:
            result = list()
            for p in player_all():
                result.append({'id': p['_id'], 'name': p['nickname'], 'last_update': p['last_update'], 'ip': p.get('ip', None)})
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=29'
            return result
        elif player_id == 'me':
            if cherrypy.request.method == 'OPTIONS':
                cherrypy_cors.preflight(allowed_methods=['GET', 'PATCH'])
            if 'X-Forwarded-For' in cherrypy.request.headers:  # needs to be used in case haproxy is used in front of TAS
                player_ip = cherrypy.request.headers['X-Forwarded-For']
            else:
                player_ip = cherrypy.request.remote.ip
            if cherrypy.request.method == 'GET':
                result = player_get(player_ip=player_ip)
                if result is not None:
                    result['id'] = result.pop('_id', None)
                    result['name'] = result.pop('nickname', None)
                cherrypy.response.headers['Cache-Control'] = 'no-cache'
                return result
            elif cherrypy.request.method == 'PATCH':
                player_id = cherrypy.request.json.get('player_id', None)
                if player_id is None:
                    return {'s': 1, 'm': 'player_id missing in request'}
                s = player_update_ip(player_id=player_id, player_ip=player_ip)
                if s == 0:
                    return {'s': s, 'm': 'OK'}
                elif s == 1:
                    return {'s': s, 'm': 'invalid player'}
                elif s == 2:
                    return {'s': s, 'm': 'player does allready have an IP assigned'}
                elif s == 3:
                    return {'s': s, 'm': 'IP allready assigned to different player'}
                else:
                    return None
            else:
                return None
        else:
            player_id = unquote(player_id)
            if not details:
                result = player_get(player_id)
                if result is not None:
                    result['id'] = result.pop('_id', None)
                    result['name'] = result.pop('nickname', None)
                cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=29'
                return result
            elif details == 'rankings':
                cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=3'
                return ranking_player(player_id)
            elif details == 'laptimes':
                if challenge_id is None:
                    result = list()
                    for lt in laptime_filter(player_id=player_id):
                        lt.pop('_id', None)
                        lt.pop('player_id', None)
                        result.append(lt)
                    cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=59'
                    return result
                else:
                    result = list()
                    for lt in laptime_filter(player_id=player_id, challenge_id=challenge_id):
                        lt.pop('_id', None)
                        lt.pop('player_id', None)
                        lt.pop('challenge_id', None)
                        result.append(lt)
                    cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=29'
                    return result
            else:
                return None


@cherrypy.popargs('challenge_id')
class Rankings():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self, challenge_id=None):
        if challenge_id is None:
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=3'
            return ranking_global()
        elif challenge_get(challenge_id) is None:
            return {'m': 'invalid challenge_id'}
        else:
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=3'
            return ranking_challenge(challenge_id)


@cherrypy.popargs('replay_name')
class Replays():
    @cherrypy.expose()
    def index(self, replay_name=None):
        if replay_name is None:
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=30'
            cherrypy.response.headers['Content-Type'] = 'application/json'
            result = list()
            for laptime in laptime_filter(replay=True):
                laptime.pop('_id', None)
                result.append(laptime)
            return json.dumps(result).encode('utf-8')

        laptime = laptime_get(replay=replay_name)
        if laptime is None or not replay_exists(replay_name):
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=30'
            cherrypy.response.status = 404
            return
        else:
            def timetos(time):
                m = int(abs(time) / 10)
                ms = int(m % 100)
                m = int(m / 100)
                s = int(m % 60)
                m = int(m / 60)
                return f"{m}-{'0' if s < 10 else ''}{s}-{'0' if ms < 10 else ''}{ms}"
            player = player_get(laptime['player_id'])
            challenge = challenge_get(laptime['challenge_id'])
            created = datetime.fromtimestamp(laptime['created_at']).strftime('%Y_%m_%d_%H_%M_%S')
            filename = f"{created}_{challenge['name']}_{player['nickname']}_({timetos(laptime['time'])}).Replay.Gbx"
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=10000'
            cherrypy.response.headers['Content-Type'] = 'application/octet-stream'
            cherrypy.response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return file_generator(replay_get(replay_name))


@cherrypy.popargs('thumbnail_name')
class Thumbnails():
    @cherrypy.expose()
    def index(self, thumbnail_name=None):
        if thumbnail_name is None:
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=30'
            cherrypy.response.headers['Content-Type'] = 'application/json'
            result = list()
            for c in challenge_all():
                result.append({'challenge_id': c['_id'], 'name': c['name'], 'thumbnail': c['_id'] + '.jpg'})
            return json.dumps(result).encode('utf-8')
        if not thumbnail_exists(thumbnail_name):
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=30'
            cherrypy.response.status = 404
            return
        else:
            filename = thumbnail_name
            if not filename.endswith('.jpg'):
                filename = filename + '.jpg'
            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=10000'
            cherrypy.response.headers['Content-Type'] = 'application/octet-stream'
            cherrypy.response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return file_generator(thumbnail_get(thumbnail_name))


def periodic_ranking_rebuild_function():
    while True:
        time.sleep(5)
        current_challenge = challenge_id_get(current=True)
        if current_challenge is not None:
            ranking_rebuild(current_challenge)


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.staticdir.root': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static'),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'ang/en',
            'tools.staticdir.index': 'index.html'
        },
        '/de': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'ang/de',
            'tools.staticdir.index': 'index.html',
            'tools.staticdir.abs_index': True
        },
        '/en': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'ang/en',
            'tools.staticdir.index': 'index.html',
            'tools.staticdir.abs_index': True
        },
        '/download': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'download'
        }
    }
    config = get_config('server')
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port'], 'cors.expose.on': True})

    wait_for_mongodb_server()
    start_tmnfd_connection()
    periodic_ranking_rebuild_process = Process(target=periodic_ranking_rebuild_function, daemon=True)
    periodic_ranking_rebuild_process.start()
    start_metrics_exporter()
    cherrypy.quickstart(TimeAttackServer(), '/', conf)
