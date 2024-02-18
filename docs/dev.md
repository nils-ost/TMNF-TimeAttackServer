## Requirements

### Backend / TMNFD

```
apt install liblzo2-dev python3-dev virtualenv
```

### Frontend

Copied from [https://github.com/nodesource/distributions/blob/master/README.md](https://github.com/nodesource/distributions/blob/master/README.md)
```
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Dev Helpers

If you like to start (and stop) a dev-mongodb and dev-haproxy with a single command you can do this with having docker (or podman) installed. This can be done with:

```
curl -fsSL https://get.docker.com | sh
```

## Installs

### Backend / TMNFD

```
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Optional

Autoloads the virtualenv (venv) when you in the projectdir or a sub-dir

Add following lines to .envrc
```
source venv/bin/activate
unset PS1
```

### Frontend

```
cd tas/frontend
npm install
```

#### Optional

If you like to work with the local angular install

```
cd tas/frontend/node_modules/@angular/cli/bin
ln -s ng.js ng
```

Now you can add `PATH_add tas/frontend/node_modules/@angular/cli/bin` to your .envrc

## Others

```
pre-commit install
sudo apt install makeself
```

# v2

## Develop Config-/User-/Login-API

  * in root-dir just `invoke dev-start`
  * in tas/backend `python api-py` (by default the api connects to mongoDB on 127.0.0.1:27017 which is the dev-container listening on)
  * finally in tas/frontend do `ng serve -c wst`

A root user `admin` with password `password` is created by api.py as no users are configured on the system