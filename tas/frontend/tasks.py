from invoke import task


@task(name='build-container-image')
def build_container_image(c, version=None):
    c.run('sudo docker build -t nilsost/tas-frontend:latest .')
    if version is not None:
        c.run(f'sudo docker tag nilsost/tas-frontend:latest nilsost/tas-frontend:{version}')


@task(name='push-container-image')
def push_container_image(c, version=None):
    if version is not None:
        c.run(f'sudo docker push nilsost/tas-frontend:{version}')
    c.run('sudo docker push nilsost/tas-frontend:latest')
