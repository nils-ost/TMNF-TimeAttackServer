from invoke import task, call


@task(name="dev-start")
def start_development(c):
    r = c.run("sudo docker ps -f name=dev-mongo", hide=True)
    if 'dev-mongo' not in r.stdout:
        print("Starting mongoDB")
        c.run("sudo docker run --name dev-mongo --rm -v /media/ramdisk/mongodb:/data/db -p 27017:27017 -d mongo:4.4")
    c.run("python install/wait_for_mongodb.py")


@task(name="dev-stop")
def stop_development(c):
    for name in ['dev-mongo']:
        r = c.run(f"sudo docker ps -f name={name}", hide=True)
        if name in r.stdout:
            print(f"Stopping {name}")
            c.run(f"sudo docker stop {name}")
    print('Removing storage for dev-mongo')
    c.run('sudo rm -rf /media/ramdisk/mongodb')


@task(pre=[stop_development], post=[start_development], name="dev-clean")
def cleanup_development(c):
    pass


@task(name="ng-build")
def ng_build(c):
    c.run('rm -rf tas/backend/static/ang')
    c.run('cd tas/frontend; ng build --output-path ../backend/static/ang')


@task(pre=[ng_build], name="create-bundle")
def create_bundle(c):
    c.run('rm -rf /tmp/tmnf-tas; mkdir -p /tmp/tmnf-tas/tas/backend; mkdir -p /tmp/tmnf-tas/tmnfd; rm -rf tas/backend/helpers/__pycache__; rm -rf tmnfd/helpers/__pycache__')
    for item in ['tas/backend/timeAttackServer.py', 'tas/backend/nextChallenge.py', 'tas/backend/requirements.txt', 'tas/backend/helpers', 'tas/backend/static']:
        c.run(f"cp -r {item} /tmp/tmnf-tas/tas/backend/")
    for item in ['fabfile.py', 'install']:
        c.run(f"cp -r {item} /tmp/tmnf-tas/")
    for item in ['tmnfd/cli.py', 'tmnfd/requirements.txt', 'tmnfd/helpers']:
        c.run(f"cp -r {item} /tmp/tmnf-tas/tmnfd/")
    c.run('cp install/bundle-installer.sh /tmp/tmnf-tas/installer.sh; chmod +x /tmp/tmnf-tas/installer.sh')
    c.run('makeself /tmp/tmnf-tas ./tmnf-tas-installer.run "Installer for TMNF-TimeAttacServer" ./installer.sh')
    c.run('rm -rf /tmp/tmnf-tas')
