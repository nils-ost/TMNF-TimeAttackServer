import cherrypy
import cherrypy_cors
from cherrypy.lib.static import serve_file
import time
import os
from helpers.mongodb import challenge_all, challenge_get, challenge_id_get, player_all, player_get, ranking_global, ranking_for, ranking_player
from helpers.tmnfd import connect as start_tmnfd_connection
from helpers.config import get_config


class TimeAttackServer():
    def __init__(self):
        self.challenges = Challenges()
        self.players = Players()
        self.rankings = Rankings()


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


@cherrypy.popargs('player_id', 'details')
class Players():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self, player_id=None, details=None):
        if not player_id:
            result = list()
            for p in player_all():
                result.append({'id': p['_id'], 'name': p['nickname'], 'last_update': p['last_update']})
            return result
        else:
            if not details:
                result = player_get(player_id)
                if result is not None:
                    result['id'] = result.get('_id')
                    result.pop('_id', None)
                return result
            elif details == 'rankings':
                return ranking_player(player_id)
            else:
                return None


@cherrypy.popargs('challenge_id')
class Rankings():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self, challenge_id=None, rebuild='false'):
        if challenge_id is None:
            if rebuild == 'true':
                return ranking_global(challenge_id_get(current=True))
            else:
                return ranking_global()
        elif challenge_get(challenge_id) is None:
            return {'m': 'invalid challenge_id'}
        else:
            return ranking_for(challenge_id, challenge_id_get(current=True))


def error_page_404(status, message, traceback, version):
    path = message.split("'")
    if len(path) == 3:
        path = path[1].strip('/').split('/')
        if path[0] in ['de', 'en']:
            cherrypy.response.status = 200
            return serve_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "static/ang", path[0], 'index.html'))
    return "Page not found"


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.join(os.path.dirname(os.path.realpath(__file__)), "static"),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "ang/de",
            'tools.staticdir.index': "index.html"
        },
        '/de/*': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "ang/de",
            'tools.staticdir.index': "index.html"
        },
        '/en': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "ang/en",
            'tools.staticdir.index': "index.html"
        }
    }
    config = get_config('server')
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port'], 'cors.expose.on': True, 'error_page.404': error_page_404})

    start_tmnfd_connection()
    cherrypy.quickstart(TimeAttackServer(), '/', conf)
