#!/bin/bash

mkdir -p /cfg/Tracks/Challenges
mkdir -p /cfg/Tracks/Campaigns
cp -n /tmdedicated/GameData/Config/dedicated_cfg.txt /cfg/dedicated_cfg.txt
cp -r -n /tmdedicated/GameData/Tracks/MatchSettings/Nations /cfg/MatchSettings
cp -r -n /tmdedicated/GameData/Tracks/Campaigns/Nations /cfg/Tracks/Campaigns/Nations

python3 /app/cli --prepare-start

cp /cfg/active_ms.txt /tmdedicated/GameData/Tracks/MatchSettings/active.txt
cp /cfg/dedicated_cfg.txt /tmdedicated/GameData/Config/dedicated_cfg.txt
cp -r /cfg/Tracks/Challenges /tmdedicated/GameData/Tracks

cd /tmdedicated
./TrackmaniaServer /dedicated_cfg=dedicated_cfg.txt /game_settings=MatchSettings/active.txt /lan /nodaemon
