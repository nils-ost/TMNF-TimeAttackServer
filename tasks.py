from invoke import task
import os


@task(name='dev-start')
def start_development(c):
    r = c.run('sudo docker ps -f name=dev-mongo', hide=True)
    if 'dev-mongo' not in r.stdout:
        print('Starting mongoDB')
        c.run('sudo docker run --name dev-mongo --rm -p 27017:27017 -d mongo:4.4')

    r = c.run('sudo docker ps -f name=dev-haproxy', hide=True)
    if 'dev-haproxy' not in r.stdout:
        print('Starting HAproxy')
        c.run(f'sudo docker run --name dev-haproxy --rm -p 80:80 -p 8404:8404 -p 9999:9999 \
            -v {os.path.join(os.path.abspath(os.path.curdir), "install/haproxy.cfg")}:/usr/local/etc/haproxy/haproxy.cfg:ro \
            --add-host=host.docker.internal:host-gateway \
            --sysctl net.ipv4.ip_unprivileged_port_start=0 -d haproxy:lts-alpine')


@task(name='dev-stop')
def stop_development(c):
    for name in ['dev-mongo', 'dev-haproxy']:
        r = c.run(f'sudo docker ps -f name={name}', hide=True)
        if name in r.stdout:
            print(f'Stopping {name}')
            c.run(f'sudo docker stop {name}')


@task(pre=[stop_development], post=[start_development], name='dev-clean')
def cleanup_development(c):
    pass


@task(name='ng-build')
def ng_build(c):
    c.run('rm -rf tas/backend/static/ang')
    c.run('cd tas/frontend; ng build --output-path ../backend/static/ang')


@task(pre=[ng_build], name='create-bundle')
def create_bundle(c):
    c.run('rm -rf /tmp/tmnf-tas; mkdir -p /tmp/tmnf-tas/tas/backend; mkdir -p /tmp/tmnf-tas/tmnfd;')
    c.run('rm -rf tas/backend/helpers/__pycache__; rm -rf tmnfd/helpers/__pycache__; rm -rf tmnfd/screens/__pycache__')
    for item in ['tas/backend/timeAttackServer.py', 'tas/backend/cli.py', 'tas/backend/requirements.txt', 'tas/backend/helpers', 'tas/backend/static']:
        c.run(f'cp -r {item} /tmp/tmnf-tas/tas/backend/')
    for item in ['/tmp/tmnf-tas/tas/backend/static/download']:
        c.run(f'rm -rf {item}', warn=True)
    for item in ['fabfile.py', 'install']:
        c.run(f'cp -r {item} /tmp/tmnf-tas/')
    for item in ['tmnfd/cli.py', 'tmnfd/requirements.txt', 'tmnfd/helpers', 'tmnfd/screens']:
        c.run(f'cp -r {item} /tmp/tmnf-tas/tmnfd/')
    version = c.run('git describe')
    version = version.stdout.strip().replace('v', '', 1).rsplit('-', 1)[0].replace('-', '.')
    with open('/tmp/tmnf-tas/tas/backend/helpers/version.py', 'w') as f:
        f.write(f"version = '{version}'")
    c.run('cp install/bundle-installer.sh /tmp/tmnf-tas/installer.sh; chmod +x /tmp/tmnf-tas/installer.sh')
    c.run(f'makeself /tmp/tmnf-tas ./tmnf-tas-installer_v{version}.run "Installer for TMNF-TimeAttackServer" ./installer.sh')
    c.run('rm -rf /tmp/tmnf-tas')
