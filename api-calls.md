# API-Calls

## Public

`/challenges`

`/challenges/current`

`/challenges/next`

`/players` gives all players

`/rankings/<challenge_id>` gives ranking for challenge_id

`/rankings?rebuild=<true|false>` gives global ranking
if rebuild is true the cache for the current challenge is recaluculated befor global ranking is build
if rebuild is false or omitted the global ranking is build entirely from cached data

## Private