# Set the base image
FROM python:3.10-alpine

MAINTAINER Nils Ost

ENV HOME /app

WORKDIR $HOME

RUN apk --no-cache add git

ADD requirements.txt $HOME/requirements.txt
RUN pip3 install -r $HOME/requirements.txt

ADD helpers $HOME/helpers
ADD static $HOME/static
ADD timeAttackServer.py $HOME/main
ADD cli.py $HOME/cli
ADD dedicated-receiver.py $HOME/dreceiver
ADD dedicated-worker.py $HOME/dworker
ADD dedicated-watcher.py $HOME/dwatcher

ENTRYPOINT ["python3"]
CMD ["main"]
