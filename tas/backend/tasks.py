from invoke import task
import time


@task(name='testdata')
def generate_testdata(c):
    from helpers.mongodb import challenge_add, player_update, laptime_add
    from random import randrange
    challenge_add('cid1', 'A01', 300000, 50000, False)
    challenge_add('cid2', 'A02', 300000, 40000, False)
    challenge_add('cid3', 'A03', 300000, 30000, False)
    player_update('nijo', 'NiJO', 250)
    player_update('someone', 'Hello World', 249)
    player_update('bad', 'I suck', 248)
    for p in range(1, 11):
        player_update(f'p{p}', f'Player{p}', 248 - p)
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
        laptime_add(f'p{p}', f'cid{c}', t)


@task(name='testdata-real')
def generate_testdata_real(c):
    from helpers.mongodb import challenge_all, player_update, laptime_add
    from random import randrange
    for p in range(1, 31):
        player_update(f'p{p}', f'Player{p}', 248 - p)
    for c in challenge_all():
        rel_time = c['rel_time']
        if c['lap_race']:
            rel_time /= 3
        rel_time_s = rel_time - 5000
        rel_time += 5000
        for p in range(1, 31):
            laptime_add(f'p{p}', c['_id'], randrange(int(rel_time_s / 10), int(rel_time / 10), 1) * 10)
    time.sleep(1)
    player_update('mid', 'MiddleMan', 100)
    for c in challenge_all():
        laptime_add('mid', c['_id'], c['rel_time'])


@task(name='build-container-image')
def build_container_image(c, version=None):
    c.run('sudo docker build -t nilsost/tas:latest .')
    if version is not None:
        c.run(f'sudo docker tag nilsost/tas:latest nilsost/tas:{version}')


@task(name='push-container-image')
def push_container_image(c, version=None):
    if version is not None:
        c.run(f'sudo docker push nilsost/tas:{version}')
    c.run('sudo docker push nilsost/tas:latest')
