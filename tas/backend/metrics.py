import os
import cherrypy
import logging
from helpers.mongodb import get_players_count, get_active_players_count, get_laptimes_count, get_laptimes_sum, get_total_seen_count


class Metrics():
    @cherrypy.expose()
    def index(self):
        cherrypy.response.headers['Cache-Control'] = 'no-cache'
        cherrypy.response.headers['Content-Type'] = 'text/plain; version=0.0.4'
        return f"""
# HELP tas_players_total Total number of individual players ever connected to server
# TYPE tas_players_total counter
tas_players_total {get_players_count()}
# HELP tas_players_active Players currently playing on server
# TYPE tas_players_active gauge
tas_players_active {get_active_players_count()}
# HELP tas_laptimes_total Number of laptimes recorded by server
# TYPE tas_laptimes_total counter
tas_laptimes_total {get_laptimes_count()}
# HELP tas_laptimes_seconds_sum Times of all recorded laptimes added up
# TYPE tas_laptimes_seconds_sum counter
tas_laptimes_seconds_sum {get_laptimes_sum() / 1000.0}
# HELP tas_challenges_seen_total All seen counters of all challenges added up
# TYPE tas_challenges_seen_total counter
tas_challenges_seen_total {get_total_seen_count()}
        """


if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'INFO')
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level=loglevel)
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8001})
    cherrypy.quickstart(Metrics(), '/metrics')
