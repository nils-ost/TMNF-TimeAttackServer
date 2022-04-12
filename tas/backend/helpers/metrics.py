from helpers.config import get_config
from multiprocessing import Process

metrics_exporter_process = None


def start_metrics_exporter():
    global metrics_exporter_process

    def metrics_exporter_function():
        import cherrypy
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

        config = get_config('metrics')
        cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port']})
        cherrypy.quickstart(Metrics(), '/metrics')

    config = get_config('metrics')
    if config['enabled'] and metrics_exporter_process is None:
        metrics_exporter_process = Process(target=metrics_exporter_function, daemon=True)
        metrics_exporter_process.start()
