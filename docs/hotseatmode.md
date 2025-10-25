# HotSeat-Mode

The goal of the HotSeat-Mode is identical to the one in normal mode: To get the fastest Laptime on a given Challenge. But the Players are not able to drive all at once, instead there is only one station allowed to connect to the server. The Players now have to play in rotation on this one station: That is the HotSeat

In addition to that (and to give all Players a equal chance) there is only one Challenge played over and over in HotSeat-Mode; so everyone is just racing for the fastest Laptime on this one Challenge.

As there is just one game connected to the server (and therefor also just one play-account) the server needs a way to get told who is driving currently. If the HotSeat-Mode is enable the PlayerHUD Screen in the frontend gets replaced by the HotSeat screen. This enables Players to enter their name, refelects who the server thinks is driving currently and gives the Player some statistics on how he performs. After changing the name all new Laptimes are immediatly captured for the new Player.

## Preamble

If you now like to try out or play the HotSeat-Mode please make sure you have allready installed TMNF-TimeAttackServer as stated in the [installation instructions](install.md) and did the [initial configuration](configuration.md) (you can ommit the section `Create MatchSettings` in this generic configuration)

After this keep on going in this documentation...

## Create MatchSeattings-File (for HotSeat)

For the HotSeat-Mode any MatchSettings-File can be used, but as of the nature of this mode only the first Challenge is going to be played. Therefore you might want to create a special MatchSettings-File to be played to ensure the correct Challenge is started.

First, if you like to play a non-standard Challenge, put the corresponding Challenge GBX to: `/opt/middleware/tmnfd/dedicated/GameData/Tracks/Challenges`

After this create a MatchSettings-File with just this Challenge and activate it. The easiest way to do so is with the [Interactive MatchSettings Editor](matchsettingseditor.md).  
Just create a new file, give it a name you like, add your Challenge to be played in HotSeat-Mode, save it and finally activate it.

## Configure TMNF-TAS

Now to setup TAS-HotSeat-Mode you need to open the tas-cli via `tmnf-tas` (or shorter just `tas`)  
You might want to configure the options `Set Display Admin`, `Set Provide Replays`, `Set Start Time` and `Set End Time` all other options (besides `Set Wallboard Players Max` and `Set Wallboard Tables Max` but we come back later to them) do not effect HotSeat-Mode.

The important configuration is to enable HotSeat-Mode by issueing `Set TAS-HotSeat-Mode`.  
After this is done you might `Clear DB` (but do not clear settings) and you need to `Restart Stack`.

Congratulations you TMNF-TAS instance is now running in HotSeat-Mode.

Note: If you like to disable HotSeat-Mode again just rerun `Set TAS-HotSeat-Mode` and `Restart Stack`.

## Set up the HotSeat

As of the nature of this game-mode you will only have one station that plays on your server. And it's quiet likely you are going to set up this station. For this reason, here are my recommendations on how to set up this HotSeat station:

Grab a PC that is capable of running TMNF and has a decently modern web-browser installed.

Start TMNF in window mode (you will see why in the next step) and connect inside the game to your TMNF-TAS server.

Now open up a web-browser and navigate to the frontend of you TMNF-TAS server, here click on the HotSeat screen. In this screen the players are able to enter their name when they are taking control over the HotSeat.  
Therefore I recommend to resize the browser-window that it fits on the left or right side next to the TMNF window to make it obvious for the players to enter their name before driving.

## Set up Wallboard

Finally you might want to display all the bestlaptimes the players drove. This might be a second screen on the HotSeat PC or a projector that is capable of accessing TMNF-TAS frontend.

In any case open the frontend in a browser window and select the Wallboard screen. It's quite likely that the default settings will not use the available space as efficient as you like. But you can adjust those on-the-fly just open up the `tas` cli on your server and try out different values for `Set Wallboard Players Max` (maximum number of rows per table) and `Set Wallboard Tables Max` (maximum number of tables side-by-side). Please be aware that it might take up to 60 seconds for those changes to be applied on the wallboard as those settings are not refreshed quiet frequently.