#!/bin/bash

apt update
apt install -y python3 virtualenv
virtualenv -p /usr/bin/python3 venv
venv/bin/pip install -r install/requirements_deploy.txt

ssh-keygen -t ed25519 -f ./id_fab -N ""
cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak
cat ./id_fab.pub >> ~/.ssh/authorized_keys
cp ~/.ssh/config ~/.ssh/config.bak
echo -e "StrictHostKeyChecking no\nUserKnownHostsFile /dev/null" > ~/.ssh/config

echo -e "\n\n#####################################\nHandover to Fabric\n#####################################\n\n"
venv/bin/fab -i id_fab -H root@localhost deploy

rm ~/.ssh/authorized_keys
rm ~/.ssh/config
mv ~/.ssh/authorized_keys.bak ~/.ssh/authorized_keys
mv ~/.ssh/config.bak ~/.ssh/config
