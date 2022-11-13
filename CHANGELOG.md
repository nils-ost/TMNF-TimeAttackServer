# TMNF-TimeAttackServer Changelog

## v1.1.1

  * TAS-BE: Fixed issue with player-logins containing whitespaces crashed worker on connect ([issue#1](https://github.com/nils-ost/TMNF-TimeAttackServer/issues/1))

## v1.1.0

  * It's now possible to set a start- and end-time; before and after the Gameserver is than locked for Players
    * TAS-CLI: Options to set and delete start- and end-time
    * TAS-BE: Locks Gameserver before start-time; unlocks it after start-time and locks it again after end-time
    * TAS-FE: New screens: start-countdown and end-countdown
        * Are available when the corresponding time is set
        * Are showing wallboard sized countdowns
    * TAS-FE: Welcome screen
        * Now shows a start- or end-countdown for corresponding start- and end-time
        * Blurs buttons to all other screens before start-time
    * TAS-FE: Wallboard screen
        * Info-Box is shown when end-time is within one hour
        * Challenges-Ticker only shows upcoming Challenges if the start before end-time
        * Redirects to Players screen after end-time (to show results)
    * TAS-FE: Challenges screen 'Up' column now shows 'Tornament ended' info for all Challenges that do not start before end-time
  * Introduced a versioning system
    * Functions added to enable DB upgrades on later versions
    * The current running and the DB version are tracked and compared on server-start
    * The current running version is displayed on TAS-CLI and TAS-FE's welcome screen
  * Added functions to TAS-CLI and TMNFD-CLI to create Backups of the whole Stack and functions to restore those Backups even on a fresh installation

## v1.0.3

  * bundle-installer.sh now also installs `openssh-server` (which reduces user-preconfiguration of the system to the bare minimum)

## v1.0.2

  * bundle-installer.sh now creates `/root/.ssh` directory just in case it is not present (this caused installer crashes on servers where no SSH configuration was present for root)

## v1.0.1

  * Removed depricated option http-use-htx from haproxy.cfg
  * Fixed and cleand up systemd services
  * TAS-FE: Formatting on Challenge- and Player-Names is now removed
  * TAS-FE: pulled all the `handleError` functions from services into one central module