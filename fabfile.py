from fabric import task
import patchwork.transfers
import os
import subprocess
import time
from datetime import datetime

apt_update_run = False
project_dir = "/opt/middleware/tmnf-tas"
backup_dir = "/var/backup"
storagedir_mongo = "/var/data/mongodb"
mongodb_image = 'mongo:4.4'
mongodb_service = "docker.mongodb.service"


def docker_pull(c, image):
    print(f"Preloading docker image {image}")
    c.run(f"docker pull {image}")


def docker_prune(c):
    print("Removing all outdated docker images")
    c.run("docker image prune -f")


def systemctl_stop(c, service):
    if c.run(f"systemctl is-active {service}", warn=True, hide=True).ok:
        print(f"Stop Service {service}", flush=True)
        c.run(f"systemctl stop {service}", hide=True)


def systemctl_start(c, service):
    if not c.run(f"systemctl is-enabled {service}", warn=True, hide=True).ok:
        print(f"Enable Service {service}", flush=True)
        c.run(f"systemctl enable {service}", hide=True)
    if c.run(f"systemctl is-active {service}", warn=True, hide=True).ok:
        print(f"Restart Service {service}", flush=True)
        c.run(f"systemctl restart {service}", hide=True)
    else:
        print(f"Start Service {service}", flush=True)
        c.run(f"systemctl start {service}", hide=True)


def systemctl_start_docker(c):
    if not c.run(f"systemctl is-enabled docker", warn=True, hide=True).ok:
        print(f"Enable Service docker", flush=True)
        c.run(f"systemctl enable docker", hide=True)
    if c.run(f"systemctl is-active docker", warn=True, hide=True).ok:
        print(f"Service docker allready running", flush=True)
    else:
        print(f"Start Service docker", flush=True)
        c.run(f"systemctl start docker", hide=True)


def systemctl_install_service(c, local_file, remote_file, replace_macros):
    print(f"Installing Service {remote_file}", flush=True)
    c.put(os.path.join('install', local_file), remote=os.path.join('/etc/systemd/system', remote_file))
    for macro, value in replace_macros:
        c.run("sed -i -e 's/" + macro + "/" + value.replace('/', '\/') + "/g' " + os.path.join('/etc/systemd/system', remote_file))


def setup_virtualenv(c):
    print("Setup virtualenv for TMNF-TAS")
    c.run(f"virtualenv -p /usr/bin/python3 {os.path.join(project_dir, 'venv')}")
    print("Installing python requirements for TMNF-TAS")
    c.run(f"{os.path.join(project_dir, 'venv/bin/pip')} install -r {os.path.join(project_dir, 'requirements.txt')}")


def upload_deploy_helpers(c):
    print("Creating deploy helpers")
    c.run("mkdir -p /tmp/tmnf-tas-deploy")
    c.put("install/wait_for_mongodb.py", remote=os.path.join("/tmp/tmnf-tas-deploy", "wait_for_mongodb.py"))


def cleanup_deploy_helpers(c):
    print("Removing deploy helpers")
    c.run("rm -rf /tmp/tmnf-tas-deploy")


def upload_project_files(c):
    for f in ["timeAttackServer.py", "nextChallenge.py", "requirements.txt"]:
        print(f"Uploading {f}")
        c.put(f, remote=os.path.join(project_dir, f))
    for d in ["helpers", "static"]:
        print(f"Uploading {d}")
        patchwork.transfers.rsync(c, d, project_dir, exclude=['*.pyc', '*__pycache__'], delete=True)


def create_directorys(c):
    for d in [project_dir, storagedir_mongo, backup_dir]:
        print(f"Creating {d}")
        c.run(f"mkdir -p {d}", warn=True, hide=True)


def install_apt_package(c, package):
    global apt_update_run
    if not c.run(f"dpkg -s {package}", warn=True, hide=True).ok:
        if not apt_update_run:
            print('Running apt update')
            c.run('apt update', hide=True)
            apt_update_run = True
        print(f"Installing {package}")
        c.run(f"apt install -y {package}")
    else:
        print(f"{package} allready installed")


def install_docker(c):
    if not c.run('which docker', warn=True, hide=True).ok:
        print('Install Docker')
        c.run('curl -fsSL https://get.docker.com | sh')
    else:
        print('Docker allready installed')


def wait_for_mongodb(c):
    print("Waiting for MongoDB to be started")
    c.run(f"cd {project_dir}; {os.path.join(project_dir, 'venv/bin/python3')} /tmp/tmnf-tas-deploy/wait_for_mongodb.py")


def backup_mongodb(c):
    if c.run(f"systemctl is-active {mongodb_service}", warn=True, hide=True).ok:
        backup_path = os.path.join(backup_dir, 'mongodb-' + datetime.now().isoformat() + '.tar.gz')
        print(f"Creating backup: {backup_path}", flush=True)
        c.run(f'docker exec -t {mongodb_service} /bin/sh -c "mongodump --forceTableScan -o /backup; tar cfz /backup.tar.gz /backup; rm -rf /backup"', hide=True)
        c.run(f'docker cp {mongodb_service}:/backup.tar.gz {backup_path}', hide=True)


@task
def deploy(c):
    c.run('hostname')
    c.run('uname -a')
    install_apt_package(c, 'curl')
    install_apt_package(c, 'rsync')
    install_docker(c)
    install_apt_package(c, 'python3')
    install_apt_package(c, 'virtualenv')
    systemctl_start_docker(c)
    docker_pull(c, mongodb_image)
    upload_deploy_helpers(c)
    create_directorys(c)
    backup_mongodb(c)
    systemctl_stop(c, mongodb_service)
    upload_project_files(c)
    setup_virtualenv(c)
    systemctl_install_service(c, 'docker.service', mongodb_service, [('__additional__', ''), ('__storage__', storagedir_mongo + ':/data/db'), ('__port__', '27017:27017'), ('__image__', mongodb_image)])
    c.run("systemctl daemon-reload")
    systemctl_start(c, mongodb_service)
    wait_for_mongodb(c)
    cleanup_deploy_helpers(c)
    docker_prune(c)
