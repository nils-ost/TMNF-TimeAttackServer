# Installation

## Requirements

### Hardware

  * x86 Server or PC
    * RaspberryPi is not usable, as the TMNF-Dedicated server is only available as x86 binary
  * About 2GB of diskspace
    * Additional 500MB if you like to provide the latest version of TMNF-Client as a download
    * And additional 150MB if you like to set up all monitoring endpoints
  * 1GB of RAM should be possible (I recommend 2GB or more)

### Software

TMNF-TAS is designed to be run on Linux or more specific on a Debian derivate. So far I tested it on:

  * Ubuntu 18.04 LTS
  * Ubuntu 20.04 LTS
  * Ubuntu 22.04 LTS

Please install the OS as usual (minimal headless installation is fine), configure your network and set up SSH. SSH needs to be installed and configured to accept key-authentication for root (this is required during installation, but you don't need to configure a key allready, this is done by the installer itself)

## Install the Softwarestack

I tried to make the installation-process as easy as possible. You just need to download the latest release from GitHub, give it execution permissions and execute it as root (it's important to do it as root)

Here are the corresponding commands:

```
# become root if you aren't yet
sudo su

# switch to root's home-dir
cd

# download latest tas-installer
wget <TBD>

# rename the file (just be be more uniform with the following commands)
mv tmnf-tas-installer* tmnf-tas-installer.run

# give the installer execution permissions
chmod 744 tmnf-tas-installer.run

# execute the installer
./tmnf-tas-installer.run
```

From now on the installer is automatically doing everything for you. The full TAS Stack is installed and a basic configuration is done. Depending on the speed of your PC and internet connection this can take a while (up to 10 minutes in my tests on a slow machine and with a 50Mbit/s connection)

After the main stack is installed (and allready running) the installer asks you if you like to setup haproxy as a cache for the TAS frontend. This is not required but quiet usefully in my opinion.

In the next step the installer likes to know if you want to set up a basic set of iptables rules. These are designed to block everything except what is needed for TAS (what I recommend to do if you are using this server only for TAS). Besides this, if you did not installed haproxy in the previous step I would not recommend to let the installer set up iptables for you, instead you should do this by hand.

Finally you get asked if you like to install prometheus monitoring metrics endpoints. As useful as these are, if you are not sure to use them later on I would not recommend the installation. It is possible to do this later on. For more information about TAS monitoring you can read the following document: [TAS Monitoring](monitoring.md)

And thats it, the installer finally does a bit of garbage collection, and your TMNF-TAS server/stack is allready running and usable. But you should consider to configure some parts, as continued in this part of the docu: [TAS Configuration](configuration.md)