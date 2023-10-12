from invoke import task


@task(name='build-container-image')
def build_container_image(c, version=None):
    c.run('sudo docker build -t nilsost/tas-tmnfd:latest .')
    if version is not None:
        c.run(f'sudo docker tag nilsost/tas-tmnfd:latest nilsost/tas-tmnfd:{version}')
