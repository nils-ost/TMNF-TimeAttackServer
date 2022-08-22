# TMNF-TimeAttackServer Changelog

## v1.0.3

  * bundle-installer.sh now also installs `openssh-server` (which reduces user-preconfiguration of the system to the bare minimum)

## v1.0.2

  * bundle-installer.sh now creates `/root/.ssh` directory just in case it is not present (this caused installer crashes on servers where no SSH configuration was present for root)

## v1.0.1

  * Removed depricated option http-use-htx from haproxy.cfg
  * Fixed and cleand up systemd services
  * TAS-FE: Formatting on Challenge- and Player-Names is now removed
  * TAS-FE: pulled all the `handleError` functions from services into one central module