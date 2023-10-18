# Set the base image
FROM python:3.10-alpine

MAINTAINER Nils Ost

ENV HOME /app

WORKDIR $HOME

RUN apk --no-cache add git docker-cli

ADD requirements.txt $HOME/requirements.txt
RUN pip3 install -r $HOME/requirements.txt

ADD helpers $HOME/helpers
ADD orchestrator.py $HOME/orchestrator
ADD api.py $HOME/api
ADD cli.py $HOME/cli
ADD metrics.py $HOME/metrics
ADD dedicated-receiver.py $HOME/dreceiver
ADD dedicated-responder.py $HOME/dresponder
ADD dedicated-controller.py $HOME/dcontroller

EXPOSE 8000/tcp 8001/tcp

ENTRYPOINT ["python3"]
CMD ["api"]
