from fabric import task
import patchwork.transfers
import os
import json
import time
from datetime import datetime

apt_update_run = False
project_dir = '/opt/middleware/tmnf-tas'
backup_dir = '/var/backup'
storagedir_mongo = '/var/data/mongodb'
storagedir_minio = '/var/data/minio'
mongodb_image = 'mongo:4.4'
mongodb_service = 'docker.mongodb.service'
mongoexporter_image = 'bitnami/mongodb-exporter:0.30.0'
mongoexporter_service = 'docker.mongoexporter.service'
haproxy_image = 'haproxy:lts-alpine'
haproxy_service = 'docker.haproxy.service'
haproxy_config = '/etc/haproxy/haproxy.cfg'
tas_service = 'tmnf-tas.service'
tmnfd_dl_url = 'http://files2.trackmaniaforever.com/TrackmaniaServer_2011-02-21.zip'
tmnfd_dir = '/opt/middleware/tmnfd'
tmnfd_version = '2011-02-21'
tmnfd_zip = 'dedicated.zip'
tmnfd_service = 'tmnfd.service'
minio_service = 'minio.service'
minio_release = '2022-04-30T22-23-53Z'
minio_dir = '/opt/middleware/minio'


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


def install_minio(c):
    for d in [minio_dir, storagedir_minio]:
        print(f'Creating {d}')
        c.run(f'mkdir -p {d}', warn=True, hide=True)
    install = False
    if c.run(f"ls {os.path.join(minio_dir, 'minio')}", warn=True, hide=True).ok:
        if minio_release not in c.run(f"{os.path.join(minio_dir, 'minio')} -v", hide=True).stdout:
            print('wrong minio release is installed')
            install = True
    else:
        print('minio is not installed')
        install = True
    if install:
        print(f'Installing minio {minio_release}')
        url = f'https://dl.min.io/server/minio/release/linux-amd64/archive/minio.RELEASE.{minio_release}'
        c.run(f"curl {url} -o {os.path.join(minio_dir, 'minio')}")
        c.run(f"chmod 744 {os.path.join(minio_dir, 'minio')}")
    else:
        print('minio allready installed')


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
    for d in [project_dir]:
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


def reassign_docker_iptables_rules(c):
    docker_rules = """
    -p tcp -m conntrack --ctorigdstport 8404 --ctdir ORIGINAL -j DROP
    -p tcp -m conntrack --ctorigdstport 27017 --ctdir ORIGINAL -j DROP
    -p tcp -m conntrack --ctorigdstport 27001 --ctdir ORIGINAL -j DROP
    """
    ifaces = [iface for iface in c.run('ls /sys/class/net', hide=True).stdout.strip().split() if iface.startswith('enp') or iface.startswith('eth')]
    docker_lines = list()
    for rule in docker_rules.strip().split('\n'):
        rule = rule.strip()
        for iface in ifaces:
            do_del = c.run(f'iptables -C DOCKER-USER -i {iface} {rule}', warn=True, hide=True).ok
            c.run(f'iptables -A DOCKER-USER -i {iface} {rule}')
            if do_del:
                c.run(f'iptables -D DOCKER-USER -i {iface} {rule}')
            else:
                print(f'Adding rule v4: DOCKER-USER -i {iface} {rule}')
            docker_lines.append(f'-A DOCKER-USER -i {iface} {rule}')
    do_del = c.run('iptables -C DOCKER-USER -j RETURN', warn=True, hide=True).ok
    c.run('iptables -A DOCKER-USER -j RETURN')
    docker_lines.append('-A DOCKER-USER -j RETURN')
    if do_del:
        c.run('iptables -D DOCKER-USER -j RETURN')
    return docker_lines


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
    install_apt_package(c, 'rsyslog')
    install_apt_package(c, 'python3')
    install_apt_package(c, 'virtualenv')
    install_apt_package(c, 'git')
    create_directorys_tas(c)


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


def deploy_tmnfd_pre(c):
    install_apt_package(c, 'curl')
    install_apt_package(c, 'python3')
    install_apt_package(c, 'virtualenv')
    install_apt_package(c, 'rsync')
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


@task(name='deploy-minio')
def deploy_minio(c):
    systemctl_stop(c, minio_service)
    install_minio(c)
    systemctl_install_service(c, 'minio.service', minio_service, [
        ('__project_dir__', minio_dir),
        ('__storage__', storagedir_minio),
        ('__user__', 'tmnftas'),
        ('__password__', 'password')
    ])
    c.run('systemctl daemon-reload')
    systemctl_start(c, minio_service)


@task(name='deploy-haproxy')
def deploy_haproxy(c):
    install_apt_package(c, 'curl')
    install_docker(c)
    systemctl_start_docker(c)
    docker_pull(c, haproxy_image)
    systemctl_stop(c, haproxy_service)

    tas_config = c.run('tmnf-tas --config', warn=True, hide=True)
    if not tas_config.ok:
        print("TAS not installed, can't setup HAproxy")
        return
    tas_config = json.loads(tas_config.stdout)
    if int(tas_config['server']['port']) == 80:
        print("TAS allready occupying port 80, can't setup HAproxy")
        return
    c.run(f'mkdir -p {os.path.dirname(haproxy_config)}', hide=True)
    c.put('install/haproxy.cfg', remote=haproxy_config)
    c.run(f"sed -i 's/local_tas host.docker.internal:[0-9]*/local_tas host.docker.internal:{tas_config['server']['port']}/' {haproxy_config}")

    systemctl_install_service(c, 'docker.service', haproxy_service, [
        ('__additional__', '--add-host=host.docker.internal:host-gateway --sysctl net.ipv4.ip_unprivileged_port_start=0'),
        ('__storage__', haproxy_config + ':/usr/local/etc/haproxy/haproxy.cfg:ro'),
        ('__port__', '80:80 -p 8404:8404'),
        ('__image__', haproxy_image)
    ])
    c.run('systemctl daemon-reload')
    systemctl_start(c, haproxy_service)
    docker_prune(c)


@task(name='deploy-iptables')
def deploy_iptables(c):
    c.run('echo iptables-persistent iptables-persistent/autosave_v4 boolean true | sudo debconf-set-selections')
    c.run('echo iptables-persistent iptables-persistent/autosave_v6 boolean true | sudo debconf-set-selections')
    install_apt_package(c, 'iptables-persistent')

    rules_v4 = """
    INPUT -p udp -m udp --dport 2350 -j ACCEPT
    INPUT -p tcp -m tcp --dport 2350 -j ACCEPT
    INPUT -p tcp -m tcp --dport 3450 -j ACCEPT
    INPUT -i lo -j ACCEPT
    INPUT -p tcp -m tcp --dport 22 -j ACCEPT
    INPUT -p tcp -m tcp --dport 80 -j ACCEPT
    INPUT -i docker0 -p tcp -m tcp --dport 8000 -j ACCEPT
    INPUT -p icmp -j ACCEPT
    INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    """
    for rule in rules_v4.strip().split('\n'):
        rule = rule.strip()
        if not c.run(f'iptables -C {rule}', hide=True, warn=True).ok:
            print(f'Adding rule v4: {rule}')
            c.run(f'iptables -A {rule}')
    c.run('iptables -P INPUT DROP')
    c.run('iptables -P FORWARD DROP')

    rules_v6 = """
    INPUT -i lo -j ACCEPT
    INPUT -p tcp -m tcp --dport 22 -j ACCEPT
    INPUT -p icmp -j ACCEPT
    INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    """
    for rule in rules_v6.strip().split('\n'):
        rule = rule.strip()
        if not c.run(f'ip6tables -C {rule}', hide=True, warn=True).ok:
            print(f'Adding rule v6: {rule}')
            c.run(f'ip6tables -A {rule}')
    c.run('ip6tables -P INPUT DROP')
    c.run('ip6tables -P FORWARD DROP')

    docker_lines = reassign_docker_iptables_rules(c)

    print('Writing /etc/iptables/rules.v4')
    c.run(f'mv /etc/iptables/rules.v4 /etc/iptables/rules.v4.bak.{int(time.time())}', hide=True, warn=True)
    c.put('install/iptables.v4', remote='/etc/iptables/rules.v4')
    c.run("sed -i -e 's/###DOCKER_RULES###/" + '\\n'.join(docker_lines) + "/g' /etc/iptables/rules.v4")

    print('Writing /etc/iptables/rules.v6')
    c.run(f'mv /etc/iptables/rules.v6 /etc/iptables/rules.v6.bak.{int(time.time())}', hide=True, warn=True)
    c.put('install/iptables.v6', remote='/etc/iptables/rules.v6')


@task(name='deploy-monitoring')
def deploy_monitoring(c):
    iptables_rules = list()
    ifaces = [iface for iface in c.run('ls /sys/class/net', hide=True).stdout.strip().split() if iface.startswith('enp') or iface.startswith('eth')]

    # ask for ip of monitoring server
    monitoring_ip = input('IP of monitoring server: ').strip()

    # enable TAS metrics endpoint
    tas_config = json.loads(c.run('tmnf-tas --config', hide=True).stdout)
    if not tas_config.get('metrics', dict()).get('enabled', False):
        print('Enableing TAS metrics-endpoint')
        c.run('tmnf-tas --enablemetrics', hide=True)
        systemctl_start(c, tas_service)  # restarts the service
    iptables_rules.append(f"INPUT -p tcp -m tcp -s {monitoring_ip} --dport {tas_config['metrics']['port']} -j ACCEPT")

    # install prometheus node_exporter
    install_apt_package(c, 'prometheus-node-exporter')
    iptables_rules.append(f'INPUT -p tcp -m tcp -s {monitoring_ip} --dport 9100 -j ACCEPT')

    # install mongodb_exporter (if mongodb on same host)
    if c.run(f'systemctl is-active {mongodb_service}', warn=True, hide=True).ok:
        docker_pull(c, mongoexporter_image)
        systemctl_install_service(c, 'docker.service', mongoexporter_service, [
            ('__additional__', f'--link {mongodb_service}'),
            ('__storage__', '/dev/null:/mnt/dummy:ro'),
            ('__port__', '9216:9216'),
            ('__image__', f'{mongoexporter_image} --mongodb.uri=mongodb://{mongodb_service}:27017/admin --discovering-mode')
        ])
        c.run('systemctl daemon-reload')
        systemctl_start(c, mongoexporter_service)
        docker_prune(c)
        for iface in ifaces:
            iptables_rules.append(f'DOCKER-USER -i {iface} -p tcp -s {monitoring_ip} -m conntrack --ctorigdstport 9216 --ctdir ORIGINAL -j ACCEPT')
            iptables_rules.append(f'DOCKER-USER -i {iface} -p tcp -m conntrack --ctorigdstport 9216 --ctdir ORIGINAL -j DROP')

    # check if haproxy metrics are enabled
    if c.run(f'systemctl is-active {haproxy_service}', warn=True, hide=True).ok:
        haproxy_ports = list()
        for port in c.run(f'docker port {haproxy_service}', hide=True).stdout.strip().split('\n'):
            port = port.strip().split('/', 1)[0]
            if not port == '80' and port not in haproxy_ports:
                haproxy_ports.append(port)
        for port in haproxy_ports:
            for iface in ifaces:
                iptables_rules.append(f'DOCKER-USER -i {iface} -p tcp -s {monitoring_ip} -m conntrack --ctorigdstport {port} --ctdir ORIGINAL -j ACCEPT')

    # check if minio is installed
    if c.run(f'systemctl is-active {minio_service}', warn=True, hide=True).ok:
        iptables_rules.append(f'INPUT -p tcp -m tcp -s {monitoring_ip} --dport 9000 -j ACCEPT')

    # add iptables rules
    iptables_lines = list()
    for rule in iptables_rules:
        rule = rule.strip()
        if not c.run(f'iptables -C {rule}', hide=True, warn=True).ok:
            print(f'Adding rule v4: {rule}')
            c.run(f'iptables -A {rule}')
        iptables_lines.append(f'-A {rule}')
    reassign_docker_iptables_rules(c)
    print()
    print()
    print('Please ensure the following lines are added to /etc/iptables/rules.v4:')
    print()
    for line in iptables_lines:
        print(line)


@task
def deploy(c):
    deploy_mongodb_pre(c)
    deploy_tas_pre(c)
    deploy_tmnfd_pre(c)

    systemctl_stop(c, tas_service)
    systemctl_stop(c, tmnfd_service)
    systemctl_stop(c, mongodb_service)
    systemctl_stop(c, minio_service)
    install_minio(c)
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
    systemctl_install_service(c, 'minio.service', minio_service, [
        ('__project_dir__', minio_dir),
        ('__storage__', storagedir_minio),
        ('__user__', 'tmnftas'),
        ('__password__', 'password')
    ])
    c.run('systemctl daemon-reload')
    systemctl_start(c, mongodb_service)
    systemctl_start(c, minio_service)
    systemctl_start(c, tmnfd_service)
    systemctl_start(c, tas_service)

    deploy_mongodb_post(c)
    deploy_tmnfd_post(c)
