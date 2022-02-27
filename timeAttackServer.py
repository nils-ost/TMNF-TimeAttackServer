import cherrypy
import cherrypy_cors
import time
from helpers.mongodb import challenge_all, challenge_get, challenge_id_get, player_all, ranking_global, ranking_for
from helpers.tmnf import start_processes as start_tmnf_connection
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


class Players():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        result = list()
        for p in player_all():
            result.append({'id': p['_id'], 'name': p['nickname']})
        return result


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


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': "/home/nijo/workspace/TMNF-TimeAttack/static",
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "ang",
            'tools.staticdir.index': "index.html"
        },
        '/wallboard': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "ang",
            'tools.staticdir.index': "index.html"
        }
    }
    config = get_config('server')
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port'], 'cors.expose.on': True})

    start_tmnf_connection()
    cherrypy.quickstart(TimeAttackServer(), '/', conf)
