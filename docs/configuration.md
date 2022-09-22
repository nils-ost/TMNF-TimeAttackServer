# Configuration

## Initial

Considering you just installed the TAS stack you might want to do the following configuration steps.

### Securing the RPC connection

The TAS daemon communicates with the TMNFD server via it's RPC connection. I highly recommend to change the login credentials on the TMNFD side.

First stop both (tmnf-tas and tmnfd) services:
```
systemctl stop tmnf-tas
systemctl stop tmnfd
```

Now open the TMNFD configuration `/opt/middleware/tmnfd/dedicated_cfg.txt` and change the three passwords in the following section:
```
<authorization_levels>
        <level>
                <name>SuperAdmin</name>
                <password>SuperAdmin</password>
        </level>
        <level>
                <name>Admin</name>
                <password>Admin</password>
        </level>
        <level>
                <name>User</name>
                <password>User</password>
        </level>
</authorization_levels>
```

Please take a note of the password you've set for SuperAdmin. You now need to open the TAS configuration `/opt/middleware/tmnf-tas/config.json` and set it there aswell in the following section:
```
"tmnf-server": {
    "host": "localhost",
    "port": 5000,
    "user": "SuperAdmin",
    "password": "SuperAdmin"
},
```

Now you can start both services again and thy should use the new password for their communication.
```
systemctl start tmnfd
systemctl start tmnf-tas
```

### Customize TMNFD

In the file `/opt/middleware/tmnfd/dedicated_cfg.txt` you can customize the settings of you TMNF-Dedicated server. These are options like the name, maxplayers, callvotes and so on. The official docu for this configuration can be found here: [readme_dedicated](https://www.gamers.org/tmn/docs/readme_dedicated.html) 

Be aware that changing `xmlrpc_port` and `xmlrpc_allowremote` might break the communication with TAS. I would recommend to let them untouched.

After you did your configuration you can restart tmnfd to apply the changes: ` systemctl restart tmnfd`

### Create MatchSettings

Assuming you don't like to allways play the NationsWhite challenge-rotation you should configure your own MatchSettings.

If you like to play tracks besides the default ones you can place the gbx files in this directory: `/opt/middleware/tmnfd/dedicated/GameData/Tracks/Challenges` (feel free to create subdirectorys if you like)

For the next step you need the unique IDs of the challenges. I've created a simple helper tool to extract those. Just type `tmnfd` on the commandline and hit enter, this should launch the tmnfd-cli. Now enter 2 (List Challenges) and hit enter. This is printing all available challenges with their path and unique ID. (You might copy the whole list to have it available for the next step)

Now change to the directory `/opt/middleware/tmnfd/MatchSettings` here are all the available MatchSetting configurations stored. Just copy one of them to be used as a template for your own configuration. How these configurations work is documented here: [readme_dedicated](https://www.gamers.org/tmn/docs/readme_dedicated.html). For the challenges list you extracted the required path's and ident's in the previous step via the tmnfd-cli. Feel free to configure the MatchSettings to your needs. But be aware of the following:
As TAS is designed to be used as a TimeAttackServer on LAN-Partys the following options are allways overwritten to this values:

  * gameinfos->game_mode = 1 (TimeAttack)
  * filter->is_lan = 1 (yes)
  * filter->is_internet = 0 (no)

Finally after creating your own MatchSetting you now need to tell TMNFD to use them. Just open `/opt/middleware/tmnfd/config.json` and enter the MatchSetting's filename in the attribute `active_matchsetting`. Save the file and restart tmnfd `systemctl restart tmnfd`

## Advanced

In this section I like to explain all the possible configuration options for tmnfd and tmnf-tas daemons. To give you a indepth view of what is possible.

### TMNFD

All installed data for tmnfd is located in the directory `/opt/middleware/tmnfd`. This includes the dedicated server binary, it's configuration and MatchSettings, the configuration for the daemon and a small cli tool I've written to simplify things.

#### config.json

Located at `/opt/middleware/tmnfd/config.json` you should usually not bother with it besides setting the `active_matchsetting` attribute to point to the to-be-used MatchSetting filename.

But here is an explanation of all available attributes:

  * `config_path` Points to the 'real' path of the used dedicated_cfg.txt
  * `match_settings` Directory where MatchSettings files are searched
  * `active_path` File where the active_matchsetting file is copied to and which is loaded by the daemon
  * `challenges_path` Path where the cli tool searches for challenges
  * `active_matchsetting` Name of the MatchSetting file that should be activated on the next daemon start
  * `replays_path` Directory in which TMNF-Dedicated is storing saved replays, this path is required by tmnfd-cli to find the replays for uploading them to S3
  * `s3` Section containing the S3 connection and configuration info. By default it is confugured to use the local, by TAS installer installed, minio but it is also possible to use an external S3 if you like.
  * `init` Internal marker if initial-startup configuration is done

The attribute `init` should allways be left as true. It's main purpose is to apply some required configuration changes to the default dedicated_cfg.txt that comes with tmnf-dedicated server. (eg the server does not start if `name` is not set, for this reason `TMNF-TAS` is set as `name` if init is false during installation)

#### CLI

I wrote a small CLI tool for managing the tmnfd daemon, currently it just have a few options but I plan to expand them if I see the need for it. You can launch this CLI by typing `tmnfd` and hitting enter regardless where you are currently located in your directory tree.

Following interactive functions are available:

  * `0 Force Config Init` Ignores the `init` attribute from `config.json` and writes mandatory attributes to `dedicated_cfg.txt`
  * `1 Write Active MatchSettings` Takes `active_matchsetting` config, copies it over to the `active_path` and applys TAS's requirements to it
  * `2 List Challenges` Searches for all available Challenges and prints them with their name, path and unique ID
  * `3 Generate Thumbnails` Extracts missing thumbnails from the corresponding challange gbx and stores them in S3 to be accessed by TAS.
  * `4 Upload Challenges` Places all challenge gbx files for active MatchSetting in S3 to be accessed by TAS.
  * `5 Create Backup` Creates a Backup of the whole TMNFD configuration, including Challeges and MatchSettigns
  * `6 Restore Backup` Restores a previously created Backup from a ZIP-File

Note to the function `Write Active MatchSettings` is executed automatically when tmnfd daemon is started. So there is no need to execute it manually if you plan to restart tmnfd anyways.

### TMNF-TAS

Everything TAS related is stored under the path `/opt/middleware/tmnf-tas`. This includes the server with it's front- and backend, the configuration and static files like the TMNF-Client download.

#### config.json

Located at `/opt/middleware/tmnf-tas/config.json` and contains all the configuration for the TAS service that is required during startup.

Following sections are available:

  * `tmnf-server` Contains all attributes that define the connection to a TMNF-Dedicated server. By default it is configured to use the local, by TAS installer installed, TMNFD but it is also possible to connect to an external custom Dedicated server.
  * `mongo` Contains all attributes that define the connection to a MongoDB server. By default it is confugured to use the local, by TAS installer installed, MongoDB but it is also possible to use an external MongoDB if you like.
  * `s3` Section containing the S3 connection and configuration info. By default it is confugured to use the local, by TAS installer installed, minio but it is also possible to use an external S3 if you like.
  * `server` Contains the configuration of the TAS service it-self
    * `port` defines the port on which TAS is providing it's front- and backend
  * `metrics` TAS comes with a Prometheus metrics endpoint, this is configured in this section
    * `enabled` Whether the metrics endpoint is enabled or not
    * `port` On which port the metrics endpoint is listening
  * `challenges` Configures how long one challenge is playable before the next challenge in rotation is started
    * `least_time` Defines the time (in milliseconds) how long a challenge should last at least.
    * `least_rounds` Gives the number of rounds players should be able to drive this challenge at least.
    * `rel_time` Defines which of the challenges times should be used to calculate the time based on `least_rounds`. Possible values are: `BronzeTime`, `SilverTime`, `GoldTime` and `AuthorTime`.
  * `util` Some default values, that are only relevant when TAS is started with an empty MongoDB. These values can dynamically changed via the TAS CLI. There is no need to bother with them in `config.json`

A note to the `challenges` section. All contained config is relevant for calculating the time a challange lasts during rotation till the next challenge is started. The time_limit of a challenge is calculated as follows:
Take the as relevant defined time (`rel_time`) from a challenge and multiply it by `least_rounds` if this value is bigger than `least_time` take it as time_limit otherwise take `least_time` as time_limit.
There is one exception of this rule:
If the challenge is a multilap challenge, take `rel_time` and devide it by `nb_laps` before multiplying it by `least_rounds`.

Also be aware that the time_limits (for multilap challenges) might differ during the first rotation through the challenge pool. This is a consequence of Dedicated server's RPC data. It only delivers `nb_laps` for the **current** challenge but not for the **next** challenge. But the time_limit needs to be set before a challenge is started. For this reason multilap challenges do have `least_time` set during the first rotation. And afterwards as TAS was able to collect all `nb_laps` values, the final (correct) time_limit.

#### CLI

TAS comes with it's own interactive CLI to configure different aspects during runtime. This can be done while the service is running and changes are applied and propagated live. (eg changing variables that influence the look of the wallboard, it is not required to reload the wallboard, these changes may take up to a minute but are applied dynamically) It can be called anywhere from the command-line with the command `tas` or `tmnf-tas`.

  * `0 Stack State` Shows the state of all TAS-Stack services
  * `1 Start Stack` Starts all services of TAS-Stack
  * `2 Stop Stack` Stops all services of TAS-Stack
  * `3 Restart Stack` Restarts all services of TAS-Stack
  * `4 Set Wallboard Players Max` Sets the maximum amount of players displayed in the tables `Current Challenge` and `Global Ranking` on the wallboard screen. This can be used to utilize the maximum of the available space but avoid scrolling.
  * `5 Set Wallboard Challenges Max` Sets the maximum amount of challenges displayed in `Challenge Schedule` on wallboard screen. This can be used to optimize `Challenge Schedule` to the available horizontal space.
  * `6 Set Display Admin` With this option a responsible persion for this server can be named, that is displayed in different locations in the frontend.
  * `7 Set Display Self URL` This defines the URL that is displayed in the info-box on wallboard screen to where the players can connect to access the frontend them-selfs.
  * `8 Set Client Download URL` If you like to provide a download URL for the latest version of TMNF client on the welcome screen, this is the place to set this URL. With this option the download link can also be disabled.
  * `9 Set Provide Replays` Enables (or disables) function to automatically store Players best laptimes in S3 and provides them for download on frontend.
  * `10 Set Provide Thumbnails` Enables (or disables) Thumbnails on frontend.
  * `11 Set Provide Challenges` Enables (or disables) the option to download challenge Gbx files on frontend.
  * `12 Set Start Time` Let's you set (or delete) the time the Tournament starts. (Before this time the Gameserver get locked, that no Player can join)
  * `13 Set End Time` Let's you set (or delete) the time the Tournament ends. (After this time the Gameserver gets locked and all Players are kicked)
  * `14 Download/Provide TMNF Client` This function can be used to download the latest version of TMNF Client, store it locally and set the `Client Download URL` in one go.
  * `15 Next Challenge` This immediately starts the next challenge (or a specific one if specified in the dialog).
  * `16 Clear Player's IP` With this function the IP of a player can be reset, to make the player selectable again in PlayerHUD.
  * `17 Merge Players` This option enables you to merge the laptimes of two players into one account. This can't be undone and might lead to dataloss.
  * `18 Clear DB` This function wipes the whole database, this can't be undone! Also it's highly recommended to first stop tmnf-tas service before executing this function.
  * `19 Create Backup` Creates a Backup of all Database, Settings, Configuration and the whole TMNFD to be restored at a later point.
  * `20 Restore Backup` Restores a previously created Backup from a ZIP-File

And here we go with some notes to the functions:

##### Set Wallboard * Max

The wallboard screen is designed to be displayed via a projector during LAN-Partys. As not all projectors does have the same resolution it was quiet hard (during development) to decide how much information should be displayed on this screen. This two functions give you the option to align the player-lists and challenge ticker to your specific needs without the need to fiddle around with the sourcecode. Just try out which settings look the best on your projector.

##### Set Provide *

For all these functions it is strongly recommended to have TAS be able to call TMFD-CLI (for Replays this is mandatory). This is due to TAS not having the required data, but TMNFD does. When enableing one of those options, TAS is doing a sanity-check and tells you wether TAS is able to call TMNF-CLI or not. For Thumbnails and Challenges it is possible to enable them without a connection (in this case you have to call the corrensponding upload function on TMNFD-CLI manually). But for Replays it is not possible to enable it without a connection, as TAS needs to call TMNFD-CLI on every new best laptime.

##### Clear DB

As mentioned this wipes the whole database. (but it is optional to to keep the dynamic settings, made with CLI) Reason behind this function is, that you might want to setup and test TAS in front of your LAN-Party but start with a fresh database once the LAN-Party started.

##### Clear Player's IP

The PlayerHUD screen is designed to display player-specific information in a quiet condensed form. For that reason TAS needs to know for which player it needs to display the information. This identification is done based on the IP that is requesting player-specific information. If TAS can't find the requesting IP in it's players store it asks the user who he is and then binds this IP to this player.

Now it is possible that a player clicked on the wrong name or (for whatever reason) changed it's IP. To solve this issue the function `Clear Player's IP` can be used where the player_id of a player needs to be entered and for that account the IP attribute is cleared, what unlocks the player and makes it selectable again.

##### Merge Players

During a LAN-Party it's quiet likely that players use offline accounts to play TrackMania. Offline accounts does not come with a unique name or ID like online accounts, but rather are combinations of the stations IP and the entered username.

It might happen that a player joins the server and gives himself the name Hans, playes a while and later desides to change his name to HanZ (which preferably should be done via is displayname, but for whatever reason the account name is changed). TAS now recognizes HanZ as a new player and all laptimes driven are accociated with the new player-account HanZ whereas some records are standing for Hans.

The function `Merge Players` gives you, the Admin, the chance to merge those two Accounts into one where all the laptimes are moved to the surviving account. (BTW this would also work if the player Hans would play from two different stations)

But be aware that this is manipulating stored data, which can't be undone.

##### Set Start/End Time

With this options it is possible to limit the duration of a TimeAttack Tournaments. The GameServer is going to be locked before StartTime and after EndTime. But it is not required to define both of them, they both also work standalone.

Also it is possible to apply both times on-the-fly. If you are setting an EndTime the Tournament is going to end at this time, if you are setting a StartTime in the future the GameServer gets immediately locked and all active Players are kicked with the message, that the Tournament did not start yet.

If you like to define a start (and/or end) time before a LAN-Party the usual process would look like the following:

  * `systemctl stop tmnf-tas`
  * set start and/or end time via CLI
  * clearDB via CLI (but not the settings)
  * `systemctl start tmnf-tas`

This process starts a fresh and time-limited Tournament, be aware that all previous driven laptimes are deleted now.

If the Tournament ended and (for whatever reason) you like to unlock the GameServer again you need to perform the following actions:

  * delete end time via CLI
  * `systemctl stop tmnfd`
  * `systemctl start tmnfd`

If you just delete the end time the GameServer stays locked!