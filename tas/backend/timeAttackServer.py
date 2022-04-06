import cherrypy
import cherrypy_cors
from cherrypy.lib.static import serve_file
import time
import os
from multiprocessing import Process
from urllib.parse import unquote
from helpers.mongodb import wait_for_mongodb_server, challenge_all, challenge_get, challenge_id_get
from helpers.mongodb import player_all, player_get, player_update_ip, laptime_filter
from helpers.mongodb import ranking_global, ranking_challenge, ranking_player, ranking_rebuild
from helpers.mongodb import get_wallboard_players_max, get_wallboard_challenges_max, get_tmnfd_name
from helpers.mongodb import get_display_self_url, get_display_admin, get_client_download_url
from helpers.mongodb import get_players_count, get_active_players_count, get_laptimes_count, get_laptimes_sum, get_total_seen_count
from helpers.tmnfd import connect as start_tmnfd_connection
from helpers.config import get_config


class TimeAttackServer():
    def __init__(self):
        self.challenges = Challenges()
        self.players = Players()
        self.rankings = Rankings()
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
        return result


class Challenges():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        result = list()
        for c in challenge_all():
            result.append({'id': c['_id'], 'name': c['name'], 'seen_count': c['seen_count'], 'seen_last': c['seen_last'], 'time_limit': c['time_limit']})
        return result

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def current(self):
        c = challenge_get(current=True)
        if c is None:
            return None
        c['id'] = c['_id']
        c.pop('_id', None)
        return c

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def next(self):
        c = challenge_get(next=True)
        if c is None:
            return None
        c['id'] = c['_id']
        c.pop('_id', None)
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
            return result
        elif player_id == 'me':
            if cherrypy.request.method == 'OPTIONS':
                cherrypy_cors.preflight(allowed_methods=['GET', 'PATCH'])
            player_ip = cherrypy.request.remote.ip
            if cherrypy.request.method == 'GET':
                result = player_get(player_ip=player_ip)
                if result is not None:
                    result['id'] = result.pop('_id', None)
                    result['name'] = result.pop('nickname', None)
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
                return result
            elif details == 'rankings':
                return ranking_player(player_id)
            elif details == 'laptimes':
                if challenge_id is None:
                    result = list()
                    for lt in laptime_filter(player_id=player_id):
                        lt.pop('_id', None)
                        lt.pop('player_id', None)
                        result.append(lt)
                    return result
                else:
                    result = list()
                    for lt in laptime_filter(player_id=player_id, challenge_id=challenge_id):
                        lt.pop('_id', None)
                        lt.pop('player_id', None)
                        lt.pop('challenge_id', None)
                        result.append(lt)
                    return result
            else:
                return None


@cherrypy.popargs('challenge_id')
class Rankings():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self, challenge_id=None):
        if challenge_id is None:
            return ranking_global()
        elif challenge_get(challenge_id) is None:
            return {'m': 'invalid challenge_id'}
        else:
            return ranking_challenge(challenge_id)


def error_page_404(status, message, traceback, version):
    path = message.split("'")
    if len(path) == 3:
        path = path[1].strip('/').split('/')
        if path[0] in ['de', 'en']:
            cherrypy.response.status = 200
            f = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/ang', path[0], 'index.html')
            return serve_file(f)
    return 'Page not found'


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
            'tools.staticdir.index': 'index.html'
        },
        '/en': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'ang/en',
            'tools.staticdir.index': 'index.html'
        },
        '/thumbnails': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'thumbnails'
        },
        '/download': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'download'
        }
    }
    config = get_config('server')
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port'], 'cors.expose.on': True, 'error_page.404': error_page_404})

    wait_for_mongodb_server()
    start_tmnfd_connection()
    periodic_ranking_rebuild_process = Process(target=periodic_ranking_rebuild_function, daemon=True)
    periodic_ranking_rebuild_process.start()
    cherrypy.quickstart(TimeAttackServer(), '/', conf)
