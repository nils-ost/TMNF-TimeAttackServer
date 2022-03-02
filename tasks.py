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
    c.run('rm -rf static/ang')
    c.run('cd frontend; ng build --output-path ../static/ang')


@task(name="testdata")
def generate_testdata(c):
    from helpers.mongodb import challenge_add, player_update, laptime_add, print_all
    from random import randrange
    challenge_add('cid1', 'A01', 300000, 50000, False)
    challenge_add('cid2', 'A02', 300000, 40000, False)
    challenge_add('cid3', 'A03', 300000, 30000, False)
    player_update('nijo', 'NiJO', 250)
    player_update('someone', 'Hello World', 249)
    player_update('bad', 'I suck', 248)
    for p in range(1, 11):
        player_update(f"p{p}", f"Player{p}", 248 - p)
    laptime_add('nijo', 'cid1', 25000)
    laptime_add('someone', 'cid1', 25000)
    laptime_add('bad', 'cid1', 50000)
    laptime_add('nijo', 'cid2', 25000)
    laptime_add('someone', 'cid2', 25000)
    laptime_add('bad', 'cid2', 0)
    laptime_add('nijo', 'cid3', 25000)
    laptime_add('someone', 'cid3', 25000)
    laptime_add('bad', 'cid3', 25000)
    for i in range(100):
        p = randrange(1, 11, 1)
        c = randrange(1, 4, 1)
        t = randrange(1000, 5000, 1) * 10
        laptime_add(f"p{p}", f"cid{c}", t)
    print_all()


@task(name="testdata-real")
def generate_testdata_real(c):
    from helpers.mongodb import challenge_all, player_update, laptime_add
    from random import randrange
    for p in range(1, 11):
        player_update(f"p{p}", f"Player{p}", 248 - p)
    for c in challenge_all():
        rel_time = c['rel_time']
        if c['lap_race']:
            rel_time /= 3
        rel_time_s = rel_time - 5000
        rel_time += 5000
        for p in range(1, 11):
            laptime_add(f"p{p}", c['_id'], randrange(int(rel_time_s), int(rel_time), 1))
