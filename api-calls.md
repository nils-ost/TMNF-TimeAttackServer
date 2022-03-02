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

`/rankings/<challenge_id>` gives ranking for challenge_id

  * player_id
  * at
  * rank
  * time
  * points

`/rankings?rebuild=<true|false>` gives global ranking
if rebuild is true the cache for the current challenge is recaluculated befor global ranking is build
if rebuild is false or omitted the global ranking is build entirely from cached data

  * player_id
  * rank
  * points

## Private