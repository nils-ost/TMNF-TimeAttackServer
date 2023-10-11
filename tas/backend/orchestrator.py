import time
import logging
from datetime import datetime
from helpers.mongodb import challenge_id_get, player_update, player_all, ranking_rebuild, hotseat_player_name_set, get_hotseat_mode


def periodic_events_function():
    while True:
        time.sleep(5)
        # rebuild rankings
        current_challenge = challenge_id_get(current=True)
        if current_challenge is not None:
            ranking_rebuild(current_challenge)
        # check active players for hotseat-mode
        if get_hotseat_mode():
            ts = int(datetime.now().timestamp())
            one_playing = False
            for p in player_all():
                if p.get('connected'):
                    if (ts - p.get('ts', ts)) > 60:
                        player_update(player_id=p.get('_id'), connected=False, ts=ts)
                    else:
                        one_playing = True
            if not one_playing:
                hotseat_player_name_set(None)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level='INFO')
    periodic_events_function()
