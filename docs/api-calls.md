# API-Calls

## Public

### GET /challenges/

Returns a list of all, as active marked, Challenges elements.

#### Cache-Control

  * `public`
  * `s-maxage=90`

#### Element-Attributes

  * `id` *(string)* Challenges unique ID as used in MatchSettings
  * `name` *(string)* Name of Challenge given by author
  * `seen_count` *(integer)* How many times the Challenge was the current Challenge
  * `seen_last` *(integer)* Last time the Challenge was set as current Challenge, as UNIX-Timestamp
  * `time_limit` *(integer)* How long the Challenge stays the current Challenge, in milliseconds

### GET /challenges/{challenge_id}/

Returns a Challenge.Gbx as file-download with given id or 404 if the requested Challenge could not be found

#### Cache-Control

  * `public`
  * `s-maxage=10000`

### GET /challenges/current/

Returns information about current Challenge or `Null` if there is no current Challenge (e.g. if the dedicated server is switching Challenges)

#### Cache-Control

  * `public`
  * `s-maxage=9`

#### Attributes

  * `id` *(string)* Challenges unique ID as used in MatchSettings
  * `name` *(string)* Name of Challenge given by author
  * `seen_count` *(integer)* How many times the Challenge was the current Challenge
  * `seen_last` *(integer)* Last time the Challenge was set as current Challenge, as UNIX-Timestamp
  * `time_limit` *(integer)* How long the Challenge stays the current Challenge, in milliseconds
  * `rel_time` *(integer)* The value of relevant time, used for time_limit calculation, in milliseconds
  * `lap_race` *(boolean)* Challenge is a multilap Challenge or not
  * `nb_laps` *(integer)* Number of laps, in multilap Challenges, the rel_time is based on
  * `active` *(boolean)* If Challenge is contained in currently used MatchSettings (should allways be True)

### GET /challenges/next/

Returns information about next Challenge or `Null` if there is no next Challenge (e.g. if TAS lost connection to dedicated server)

#### Cache-Control

  * `public`
  * `s-maxage=9`

#### Attributes

  * `id` *(string)* Challenges unique ID as used in MatchSettings
  * `name` *(string)* Name of Challenge given by author
  * `seen_count` *(integer)* How many times the Challenge was the current Challenge
  * `seen_last` *(integer)* Last time the Challenge was set as current Challenge, as UNIX-Timestamp
  * `time_limit` *(integer)* How long the Challenge stays the current Challenge, in milliseconds
  * `rel_time` *(integer)* The value of relevant time, used for time_limit calculation, in milliseconds
  * `lap_race` *(boolean)* Challenge is a multilap Challenge or not
  * `nb_laps` *(integer)* Number of laps, in multilap Challenges, the rel_time is based on
  * `active` *(boolean)* If Challenge is contained in currently used MatchSettings (should allways be True)

### GET /players/

Returns a list of all Player elements present on server

#### Cache-Control

  * `public`
  * `s-maxage=29`

#### Element-Attributes
  
  * `id` *(string)* Internally used unique ID of Player
  * `name` *(string)* Ingame nickname of Player
  * `last_update` *(integer)* At which time TAS recognized the last activity of Player, as UNIX-Timestamp
  * `ip` *(string)* IP of Players computer (or `Null` if not recognized or set)

### GET /players/{player_id}/

Returns details for single Player, or `Null` if given player_id can't be found on server

#### Cache-Control

  * `public`
  * `s-maxage=29`

#### Attributes

  * `id` *(string)* Internally used unique ID of Player
  * `name` *(string)* Ingame nickname of Player
  * `last_update` *(integer)* At which time TAS recognized the last activity of Player, as UNIX-Timestamp
  * `current_uid` *(integer)* UID TMNF-Dedicated server has currently assigned to Player
  * `ip` *(string)* IP of Players computer (or `Null` if not recognized or set)

### GET /players/me/

Returns player with the same IP as the request is made from (or `Null` if no corresponding Player is found)

#### Cache-Control

  * `no-cache`

#### Attributes

  * `id` *(string)* Internally used unique ID of Player
  * `name` *(string)* Ingame nickname of Player
  * `last_update` *(integer)* At which time TAS recognized the last activity of Player, as UNIX-Timestamp
  * `current_uid` *(integer)* UID TMNF-Dedicated server has currently assigned to Player
  * `ip` *(string)* IP of Players computer (or `Null` if not recognized or set)
  
### PATCH /players/me/

Assigns the requesting IP to the, in playload, given Player.

! Ensure the tailing /

#### Request Data

JSON-Document with following Attributes:

  * `player_id` *(string)* Internally used unique ID of Player

#### Response Data

JSON-Document with following Attributes:

  * `s` *(integer)* Return state
  * `m` *(string)* Message describing state

##### Possible States

Following states are possible to be returned:

  * `0` Operation executed as requested
  * `1` player_id is missing in request data or invalid player_id
  * `2` Player does allready have a IP assigned
  * `3` IP allready assigned to a different Player

### GET /players/hotseat/

Returns the current TAS-HotSeat-Mode Player (or `Null` if HotSeat-Mode is not enabled or no Player-name is set currently)

#### Cache-Control

  * `no-cache`

#### Attributes

  * `id` *(string)* Internally used unique ID of Player
  * `name` *(string)* Ingame nickname of Player
  * `last_update` *(integer)* At which time TAS recognized the last activity of Player, as UNIX-Timestamp
  * `current_uid` *(integer)* UID TMNF-Dedicated server has currently assigned to Player
  * `ip` *(string)* IP of Players computer (should allways be `Null` in this case)

### PATCH /players/hotseat/

Assigns the, in payload, given name as the new hotseat Player.

! Ensure the tailing /

#### Request Data

JSON-Document with following Attributes:

  * `name` *(string)* Name of the new Player

#### Response Data

JSON-Document with following Attributes:

  * `s` *(integer)* Return state
  * `m` *(string)* Message describing state

##### Possible States

Following states are possible to be returned:

  * `0` Operation executed as requested
  * `1` The TAS-HotSeat-Mode not enabled
  * `2` name is missing in request data
  * `3` invalid character in name (validation error)


### GET /players/{player_id}/rankings/

Returns a list of all Players challenge ranking elements for given player_id

#### Cache-Control

  * `public`
  * `s-maxage=3`

#### Element-Attributes

  * `challenge_id` *(string)* Challenges unique ID as used in MatchSettings
  * `at` *(integer)* At which time the Player drove it's best Laptime on Challenge, as UNIX-Timestamp
  * `rank` *(integer)* Challenge rank of this Player
  * `time` *(integer)* Best Laptime of Player on Challenge, in milliseconds
  * `points` *(integer)* Challenge points of this Player

### GET /players/{player_id}/laptimes/

Returns a list of all Laptime elements for given player_id 

#### Cache-Control

  * `public`
  * `s-maxage=59`

#### Element-Attributes

  * `challenge_id` *(string)* Challenges unique ID as used in MatchSettings
  * `time` *(integer)* Laptime of Player on Challenge, in milliseconds
  * `created_at` *(integer)* At which time the Player drove Laptime on Challenge, as UNIX-Timestamp
  * `replay` *(string)* Name of replay for laptime as it is stored in S3; `Null` if no replay is available

### GET /players/{player_id}/laptimes/{challenge_id}/

Returns a list of all Laptime elements of given player_id for given challenge_id

#### Cache-Control

  * `public`
  * `s-maxage=29`

#### Element-Attributes

  * `time` *(integer)* Laptime of Player on Challenge, in milliseconds
  * `created_at` *(integer)* At which time the Player drove Laptime on Challenge, as UNIX-Timestamp
  * `replay` *(string)* Name of replay for laptime as it is stored in S3; `Null` if no replay is available

### GET /rankings/{challenge_id}/

Returns a list of all Players challenge ranking elements for given challenge_id

#### Cache-Control

  * `public`
  * `s-maxage=3`

#### Element-Attributes

  * `player_id` *(string)* Internally used unique ID of Player
  * `at` *(integer)* At which time the Player drove it's best Laptime on Challenge, as UNIX-Timestamp
  * `rank` *(integer)* Challenge rank of this Player
  * `time` *(integer)* Best Laptime of Player on Challenge, in milliseconds
  * `points` *(integer)* Challenge points of this Player

### GET /rankings/

Returns a list of all Players global ranking elements

#### Cache-Control

  * `public`
  * `s-maxage=3`

#### Element-Attributes

  * `player_id` *(string)* Internally used unique ID of Player
  * `rank` *(integer)* Global rank of this Player
  * `points` *(integer)* Global points of this Player

### GET /replays/

Returns a list of all Laptimes that have a Replay

#### Cache-Control

  * `public`
  * `s-maxage=30`

#### Element-Attributes

  * `player_id` *(string)* Internally used unique ID of Player
  * `challenge_id` *(string)* Challenges unique ID as used in MatchSettings
  * `time` *(integer)* Laptime of Player on Challenge, in milliseconds
  * `created_at` *(integer)* At which time the Player drove Laptime on Challenge, as UNIX-Timestamp
  * `replay` *(string)* Name of replay for laptime as it is stored in S3

### GET /replays/{replay_name}/

Returns a Replay as file-download with given name or 404 if the requested Replay could not be found

#### Cache-Control

  * `public`
  * `s-maxage=10000`

### GET /thumbnails/

Returns a list of all Thumbnails with their related Challenge info

#### Cache-Control

  * `public`
  * `s-maxage=30`

#### Element-Attributes

  * `challenge_id` *(string)* Challenges unique ID as used in MatchSettings
  * `name` *(string)* Name of Challenge given by author
  * `thumbnail` *(string)* Name of thumbnail as it is stored in S3

### GET /thumbnails/{thumbnail_name}/

Returns a Thumbnail as file-download with given name or 404 if the requested Thumbnail could not be found

#### Cache-Control

  * `public`
  * `s-maxage=10000`

### GET /settings/

Returns dynamic settings

#### Cache-Control

  * `public`
  * `s-maxage=59`

#### Attributes

  * `version` *(string)* Returns the Version the Database (and TMNF-TAS) is running on
  * `wallboard_players_max` *(integer)* Maximum number of Players displayed on wallboard
  * `wallboard_challenges_max` *(integer)* Maximum number of Challenges displayer in challenges-ticker on wallboard
  * `tmnfd_name` *(string)* Ingame name of TMNF-Dedicated server
  * `display_self_url` *(string)* URL that should point to the TAS website (or `Null` if not set)
  * `display_admin` *(string)* What is displayed as the server-admin contact (or `Null` if not set)
  * `client_download_url` *(string)* URL pointing to TMNF-Client installer (or `Null` if not set)
  * `provide_replays` *(boolean)* Indicates if replay files are provided or not
  * `provide_thumbnails` *(boolean)* Indicates if challenge thumbnail files are provided or not
  * `provide_challenges` *(boolean)* Indicates if challenge Gbx files are provided or not
  * `start_time` *(integer)* Timestamp at which the Tournament starts (or `Null` if not set)
  * `end_time` *(integer)* Timestamp at which the Tournament ends (or `Null` if not set)
  * `hotseat_mode` *(boolean)* Indicates if server is running in TAS-HotSeat-Mode or not

### GET /stats/

Returns current stats of stuff happening on server

#### Cache-Control

  * `public`
  * `s-maxage=29`

#### Attributes

  * `total_players` *(integer)* the number of individual players ever joined to server
  * `active_players` *(integer)* the number of players currently playing on server
  * `laptimes_count` *(integer)* the summed up count of all laptimes by all players on all challenges
  * `laptimes_sum` *(integer)* the summed up time of all laptimes by all players on all challenges in milliseconds
  * `challenges_total_seen_count` *(integer)* summed up see_count of all challenges

## Private