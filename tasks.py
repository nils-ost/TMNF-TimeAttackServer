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


@task(name="testdata")
def generate_testdata(c):
    from helpers.mongodb import challenge_add, player_update, laptime_add, print_all
    from random import randrange
    challenge_add('cid1', 'A01')
    challenge_add('cid2', 'A02')
    challenge_add('cid3', 'A03')
    player_update('nijo', 'NiJO', 250)
    player_update('someone', 'Hello World', 249)
    player_update('bad', 'I suck', 248)
    laptime_add('bad', 'cid1', 50000)
    laptime_add('bad', 'cid2', 0)
    for c in ['cid1', 'cid2', 'cid3']:
        for p in ['nijo', 'someone']:
            for i in range(10):
                laptime_add(p, c, randrange(1000, 5000, 1) * 10)
    print_all()
