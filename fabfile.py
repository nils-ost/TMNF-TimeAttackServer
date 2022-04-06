from fabric import task
import patchwork.transfers
import os
from datetime import datetime

apt_update_run = False
project_dir = '/opt/middleware/tmnf-tas'
backup_dir = '/var/backup'
storagedir_mongo = '/var/data/mongodb'
mongodb_image = 'mongo:4.4'
mongodb_service = 'docker.mongodb.service'
tas_service = 'tmnf-tas.service'
tmnfc_dl_url = 'http://files.trackmaniaforever.com/tmnationsforever_setup.exe'
tmnfc_dir = 'static/download'
tmnfc_exe = 'tmnf_client.exe'
tmnfd_dl_url = 'http://files2.trackmaniaforever.com/TrackmaniaServer_2011-02-21.zip'
tmnfd_dir = '/opt/middleware/tmnfd'
tmnfd_version = '2011-02-21'
tmnfd_zip = 'dedicated.zip'
tmnfd_service = 'tmnfd.service'


def docker_pull(c, image):
    print(f'Preloading docker image {image}')
    c.run(f'docker pull {image}')


def docker_prune(c):
    print('Removing all outdated docker images')
    c.run('docker image prune -f')


def systemctl_stop(c, service):
    if c.run(f'systemctl is-active {service}', warn=True, hide=True).ok:
        print(f'Stop Service {service}', flush=True)
        c.run(f'systemctl stop {service}', hide=True)


def systemctl_start(c, service):
    if not c.run(f'systemctl is-enabled {service}', warn=True, hide=True).ok:
        print(f'Enable Service {service}', flush=True)
        c.run(f'systemctl enable {service}', hide=True)
    if c.run(f'systemctl is-active {service}', warn=True, hide=True).ok:
        print(f'Restart Service {service}', flush=True)
        c.run(f'systemctl restart {service}', hide=True)
    else:
        print(f'Start Service {service}', flush=True)
        c.run(f'systemctl start {service}', hide=True)


def systemctl_start_docker(c):
    if not c.run('systemctl is-enabled docker', warn=True, hide=True).ok:
        print('Enable Service docker', flush=True)
        c.run('systemctl enable docker', hide=True)
    if c.run('systemctl is-active docker', warn=True, hide=True).ok:
        print('Service docker allready running', flush=True)
    else:
        print('Start Service docker', flush=True)
        c.run('systemctl start docker', hide=True)


def systemctl_install_service(c, local_file, remote_file, replace_macros):
    print(f'Installing Service {remote_file}', flush=True)
    c.put(os.path.join('install', local_file), remote=os.path.join('/etc/systemd/system', remote_file))
    for macro, value in replace_macros:
        c.run("sed -i -e 's/" + macro + '/' + value.replace('/', r'\/') + "/g' " + os.path.join('/etc/systemd/system', remote_file))


def install_rsyslog(c):
    print('Configuring rsyslog for TMNF-TAS')
    c.put('install/rsyslog.conf', '/etc/rsyslog.d/tmnf-tas.conf')
    systemctl_start(c, 'rsyslog')


def install_logrotate(c):
    print('Configuring logrotate for TMNF-TAS')
    c.put('install/logrotate', '/etc/logrotate.d/tmnf-tas')
    c.run('chmod 644 /etc/logrotate.d/tmnf-tas')


def setup_virtualenv(c, pdir):
    print(f'Setup virtualenv for {pdir}')
    c.run(f"virtualenv -p /usr/bin/python3 {os.path.join(pdir, 'venv')}")
    print(f'Installing python requirements for {pdir}')
    c.run(f"{os.path.join(pdir, 'venv/bin/pip')} install -r {os.path.join(pdir, 'requirements.txt')}")


def upload_project_files(c):
    for f in ['timeAttackServer.py', 'cli.py', 'requirements.txt']:
        print(f'Uploading {f}')
        c.put(os.path.join('tas/backend', f), remote=os.path.join(project_dir, f))
    for d in ['tas/backend/helpers']:
        print(f'Uploading {d}')
        patchwork.transfers.rsync(c, d, project_dir, exclude=['*.pyc', '*__pycache__'], delete=True)
    for d in ['tas/backend/static/ang']:
        print(f'Uploading {d}')
        patchwork.transfers.rsync(c, d, os.path.join(project_dir, 'static'), exclude=['*.pyc', '*__pycache__'], delete=True)


def prepare_tas_cli(c):
    c.run(f"echo -e '#!/bin/bash\n{os.path.join(project_dir, 'venv/bin/python')} {os.path.join(project_dir, 'cli.py')} $*' > /usr/bin/tmnf-tas")
    c.run(f"echo -e '#!/bin/bash\n{os.path.join(project_dir, 'venv/bin/python')} {os.path.join(project_dir, 'cli.py')} $*' > /usr/bin/tas")
    c.run('chmod 755 /usr/bin/tmnf-tas')
    c.run('chmod 755 /usr/bin/tas')


def upload_tmnfd_files(c):
    for f in ['cli.py', 'requirements.txt']:
        print(f'Uploading {f}')
        c.put(os.path.join('tmnfd', f), remote=os.path.join(tmnfd_dir, f))
    for d in ['tmnfd/helpers']:
        print(f'Uploading {d}')
        patchwork.transfers.rsync(c, d, tmnfd_dir, exclude=['*.pyc', '*__pycache__'], delete=True)


def prepare_tmnfd_cli(c):
    c.run(f"echo -e '#!/bin/bash\n{os.path.join(tmnfd_dir, 'venv/bin/python')} {os.path.join(tmnfd_dir, 'cli.py')} $*' > /usr/bin/tmnfd")
    c.run('chmod 755 /usr/bin/tmnfd')
    c.run(f"{os.path.join(tmnfd_dir, 'venv/bin/python')} {os.path.join(tmnfd_dir, 'cli.py')} --init")


def create_directorys_mongodb(c):
    for d in [storagedir_mongo, backup_dir]:
        print(f'Creating {d}')
        c.run(f'mkdir -p {d}', warn=True, hide=True)


def create_directorys_tas(c):
    for d in [project_dir + '/static/thumbnails']:
        print(f'Creating {d}')
        c.run(f'mkdir -p {d}', warn=True, hide=True)


def create_directorys_tmnfd(c):
    for d in [tmnfd_dir]:
        print(f'Creating {d}')
        c.run(f'mkdir -p {d}', warn=True, hide=True)


def install_apt_package(c, package):
    global apt_update_run
    if not c.run(f'dpkg -s {package}', warn=True, hide=True).ok:
        if not apt_update_run:
            print('Running apt update')
            c.run('apt update', hide=True)
            apt_update_run = True
        print(f'Installing {package}')
        c.run(f'apt install -y {package}')
    else:
        print(f'{package} allready installed')


def install_docker(c):
    if not c.run('which docker', warn=True, hide=True).ok:
        print('Install Docker')
        c.run('curl -fsSL https://get.docker.com | sh')
    else:
        print('Docker allready installed')


def backup_mongodb(c):
    if c.run(f'systemctl is-active {mongodb_service}', warn=True, hide=True).ok:
        backup_path = os.path.join(backup_dir, 'mongodb-' + datetime.now().isoformat() + '.tar.gz')
        print(f'Creating backup: {backup_path}', flush=True)
        c.run(f'docker exec -t {mongodb_service} /bin/sh -c "mongodump --forceTableScan -o /backup; tar cfz /backup.tar.gz /backup; rm -rf /backup"', hide=True)
        c.run(f'docker cp {mongodb_service}:/backup.tar.gz {backup_path}', hide=True)


def tmnfc_provide(c):
    c.run(f'mkdir -p {os.path.join(project_dir, tmnfc_dir)}')
    tmnfc = c.run(f"cat {os.path.join(project_dir, tmnfc_dir, 'tmnfc')}", warn=True, hide=True)
    if tmnfc.ok:
        if tmnfc.stdout.strip() == 'provided':
            print('TMNF-Client allready provided')
            return
    print('Providing TMNF-Client EXE')
    c.run(f'curl {tmnfc_dl_url} --output {os.path.join(project_dir, tmnfc_dir, tmnfc_exe)}')
    c.run(f"echo 'provided' > {os.path.join(project_dir, tmnfc_dir, 'tmnfc')}")


def tmnfd_version_matches(c):
    version = c.run(f"cat {os.path.join(tmnfd_dir, 'version')}", warn=True, hide=True)
    if version.ok:
        if version.stdout.strip() == tmnfd_version:
            print('Installed TMNF-Dedicated version is allready desired version')
            return True
    return False


def tmnfd_zip_download(c):
    print('Downloading TMNF-Dedicated ZIP')
    c.run(f'curl {tmnfd_dl_url} --output {os.path.join(tmnfd_dir, tmnfd_zip)}')


def tmnfd_zip_delete(c):
    print('Removing TMNF-Dedicated ZIP')
    c.run(f'rm {os.path.join(tmnfd_dir, tmnfd_zip)}', warn=True, hide=True)


def tmnfd_zip_extract(c):
    c.run(f"rm -rf {os.path.join(tmnfd_dir, 'dedicated')}", warn=True, hide=True)
    print('Extracting TMNF-Dedicated ZIP')
    c.run(f"7z x {os.path.join(tmnfd_dir, tmnfd_zip)} -o{os.path.join(tmnfd_dir, 'dedicated')}")
    c.run(f"rm {os.path.join(tmnfd_dir, 'dedicated', 'TrackmaniaServer.exe')}")
    c.run(f"echo '{tmnfd_version}' > {os.path.join(tmnfd_dir, 'version')}")


def tmnfd_map_config(c):
    c.run(f"rm {os.path.join(tmnfd_dir, 'dedicated_cfg.txt')}", warn=True, hide=True)
    c.run(f"rm {os.path.join(tmnfd_dir, 'MatchSettings')}", warn=True, hide=True)
    c.run(f"ln -s {os.path.join(tmnfd_dir, 'dedicated/GameData/Config/dedicated_cfg.txt')} {os.path.join(tmnfd_dir, 'dedicated_cfg.txt')}")
    c.run(f"cp -r {os.path.join(tmnfd_dir, 'dedicated/GameData/Tracks/MatchSettings/Nations')} \
        {os.path.join(tmnfd_dir, 'dedicated/GameData/Tracks/MatchSettings/TAS')}")
    c.run(f"ln -s {os.path.join(tmnfd_dir, 'dedicated/GameData/Tracks/MatchSettings/TAS')} {os.path.join(tmnfd_dir, 'MatchSettings')}")


def deploy_mongodb_pre(c):
    install_apt_package(c, 'curl')
    install_docker(c)
    systemctl_start_docker(c)
    docker_pull(c, mongodb_image)
    create_directorys_mongodb(c)
    backup_mongodb(c)


def deploy_mongodb_post(c):
    docker_prune(c)


@task(name='deploy-mongodb')
def deploy_mongodb(c):
    deploy_mongodb_pre(c)

    systemctl_stop(c, mongodb_service)
    systemctl_install_service(c, 'docker.service', mongodb_service, [
        ('__additional__', ''),
        ('__storage__', storagedir_mongo + ':/data/db'),
        ('__port__', '27017:27017'),
        ('__image__', mongodb_image)
    ])
    c.run('systemctl daemon-reload')
    systemctl_start(c, mongodb_service)

    deploy_mongodb_post(c)


def deploy_tas_pre(c):
    install_apt_package(c, 'rsync')
    install_apt_package(c, 'python3')
    install_apt_package(c, 'virtualenv')
    create_directorys_tas(c)


def deploy_tas_post(c):
    tmnfc_provide(c)


@task(name='deploy-tas')
def deploy_tas(c):
    deploy_tas_pre(c)

    systemctl_stop(c, tas_service)
    upload_project_files(c)
    setup_virtualenv(c, project_dir)
    prepare_tas_cli(c)
    install_rsyslog(c)
    install_logrotate(c)
    systemctl_install_service(c, 'tmnf-tas.service', tas_service, [('__project_dir__', project_dir)])
    c.run('systemctl daemon-reload')
    systemctl_start(c, tas_service)

    deploy_tas_post(c)


def deploy_tmnfd_pre(c):
    install_apt_package(c, 'curl')
    install_apt_package(c, 'p7zip-full')
    install_apt_package(c, 'liblzo2-dev')
    install_apt_package(c, 'python3-dev')
    install_apt_package(c, 'build-essential')
    install_apt_package(c, 'imagemagick')
    create_directorys_tmnfd(c)


def deploy_tmnfd_post(c):
    tmnfd_zip_delete(c)


@task(name='deploy-tmnfd')
def deploy_tmnfd(c):
    deploy_tmnfd_pre(c)

    systemctl_stop(c, tmnfd_service)
    if not tmnfd_version_matches(c):
        tmnfd_zip_download(c)
        tmnfd_zip_extract(c)
        tmnfd_map_config(c)
    upload_tmnfd_files(c)
    setup_virtualenv(c, tmnfd_dir)
    prepare_tmnfd_cli(c)
    systemctl_install_service(c, 'tmnfd.service', tmnfd_service, [('__project_dir__', tmnfd_dir)])
    c.run('systemctl daemon-reload')
    systemctl_start(c, tmnfd_service)

    deploy_tmnfd_post(c)


@task
def deploy(c):
    deploy_mongodb_pre(c)
    deploy_tas_pre(c)
    deploy_tmnfd_pre(c)

    systemctl_stop(c, tas_service)
    systemctl_stop(c, tmnfd_service)
    systemctl_stop(c, mongodb_service)
    upload_project_files(c)
    setup_virtualenv(c, project_dir)
    prepare_tas_cli(c)
    install_rsyslog(c)
    install_logrotate(c)
    if not tmnfd_version_matches(c):
        tmnfd_zip_download(c)
        tmnfd_zip_extract(c)
        tmnfd_map_config(c)
    upload_tmnfd_files(c)
    setup_virtualenv(c, tmnfd_dir)
    prepare_tmnfd_cli(c)
    systemctl_install_service(c, 'tmnf-tas.service', tas_service, [('__project_dir__', project_dir)])
    systemctl_install_service(c, 'tmnfd.service', tmnfd_service, [('__project_dir__', tmnfd_dir)])
    systemctl_install_service(c, 'docker.service', mongodb_service, [
        ('__additional__', ''),
        ('__storage__', storagedir_mongo + ':/data/db'),
        ('__port__', '27017:27017'),
        ('__image__', mongodb_image)
    ])
    c.run('systemctl daemon-reload')
    systemctl_start(c, mongodb_service)
    systemctl_start(c, tmnfd_service)
    systemctl_start(c, tas_service)

    deploy_tas_post(c)
    deploy_mongodb_post(c)
    deploy_tmnfd_post(c)
