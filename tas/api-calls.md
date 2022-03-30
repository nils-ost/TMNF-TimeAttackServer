# API-Calls

## Public

`/challenges`

  * id
  * name
  * seen_count
  * seen_last
  * time_limit

`/challenges/current`

  * id
  * name
  * seen_count
  * seen_last
  * time_limit
  * rel_time
  * lap_race
  * nb_laps
  * active

`/challenges/next`

`/players` gives all players

  * id
  * name
  * last_update
  * ip

`/players/<player_id>` gives details for player_id

  * id
  * name
  * last_update
  * current_uid
  * ip

`/players/me/` GET returns player with the same IP as the request is made from; PATCH sets the IP of given player to the one the request is made from

GET-Return:

  * id
  * name
  * last_update
  * current_uid
  * ip

PATCH-Data:

`{"player_id": "<id>"}`

! Ensure the trailing /

`/players/<player_id>/rankings` gives all rankings of player_id

  * challenge_id
  * at
  * rank
  * time
  * points

`/players/<player_id>/laptimes` gives all laptimes of player_id

  * challenge_id
  * time
  * created_at

`/players/<player_id>/laptimes/<challenge_id>` gives all laptimes of player_id for challenge_id

  * time
  * created_at

`/rankings/<challenge_id>` gives ranking for challenge_id

  * player_id
  * at
  * rank
  * time
  * points

`/rankings` gives global ranking for all players

  * player_id
  * rank
  * points

`/settings` returns dynamic settings

  * wallboard_players_max
  * wallboard_challenges_max
  * tmnfd_name
  * display_self_url
  * display_admin
  * client_download_url

`/stats` returns current stats of stuff happening on server

  * total_players  *- the number of individual players ever joined to server*
  * active_players  *- the number of players currently playing on server*
  * laptimes_count  *- the summed up count of all laptimes by all players on all challenges*
  * laptimes_sum  *- the summed up time of all laptimes by all players on all challenges*
  * challenges_total_seen_count  *- summed up see_count of all challenges*

## Private