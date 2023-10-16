#!/bin/bash

mkdir -p /cfg
mkdir -p /tracks/Challenges
mkdir -p /tracks/Campaigns
cp -n /tmdedicated/GameData/Config/dedicated_cfg.txt /cfg/dedicated_cfg.txt
cp -r -n /tmdedicated/GameData/Tracks/MatchSettings/Nations /tracks/MatchSettings
cp -r -n /tmdedicated/GameData/Tracks/Campaigns/Nations /tracks/Campaigns/Nations

if ! python3 /app/cli --prepare-start; then
    exit 1
fi

cp /cfg/active_ms.txt /tmdedicated/GameData/Tracks/MatchSettings/active.txt
cp /cfg/dedicated_cfg.txt /tmdedicated/GameData/Config/dedicated_cfg.txt
cp -r /tracks/Challenges /tmdedicated/GameData/Tracks

cd /tmdedicated
./TrackmaniaServer /dedicated_cfg=dedicated_cfg.txt /game_settings=MatchSettings/active.txt /lan /nodaemon
