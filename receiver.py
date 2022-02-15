from datetime import datetime
import json
import sys
from helpers.GbxRemote import GbxRemote

host = '192.168.56.200'
port = 5000

receiver = GbxRemote(host, port, 'SuperAdmin', 'SuperAdmin')

while True:
    func, params = receiver.receiveCallback()

    if func == 'TrackMania.PlayerFinish':
        player_id, player_login, player_time = params
        if player_time > 0:
            print(f"{player_login} drove: {player_time / 1000}")
    elif func == 'TrackMania.BeginRace':
        print(f"Beginning: {json.dumps(params[0], indent=2)}")
    elif func == 'TrackMania.EndRace':
        print(f"Ending: {params[1]['Name']}")
    elif func == 'TrackMania.PlayerInfoChanged':
        player = params[0]
        print(f"{player['PlayerId']} is now: {player['NickName']} ({player['Login']})")

