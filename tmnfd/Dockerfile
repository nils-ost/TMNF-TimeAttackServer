FROM ubuntu:22.04 AS downloads

ENV USER root
ENV HOME /tmdedicated
ENV FILE_TMD http://files2.trackmaniaforever.com/TrackmaniaServer_2011-02-21.zip
ENV FILE_NCONVERT https://download.xnview.com/NConvert-linux64.tgz

WORKDIR $HOME

RUN apt update \
 && apt install -y --no-install-recommends ca-certificates curl unzip tar

RUN curl $FILE_NCONVERT --output nconvert.tar --silent \
 && tar xf nconvert.tar \
 && mv NConvert/nconvert /usr/bin \
 && rm -r nconvert.tar NConvert

RUN curl $FILE_TMD --output archive.zip --silent \
 && unzip archive.zip \
 && rm archive.zip



FROM python:3.10-slim-bookworm AS build

ENV USER root
ENV HOME /app

WORKDIR $HOME

RUN apt update \
 && apt install -y liblzo2-dev python3-dev build-essential

COPY requirements.txt .

RUN pip3 install --user -r requirements.txt



FROM python:3.10-slim-bookworm

ENV USER root
ENV HOME /app

WORKDIR $HOME

RUN apt update \
 && apt install -y liblzo2-2 \
 && rm -rf /var/cache/apt

COPY start.sh ./start.sh
RUN chmod +x ./start.sh
COPY --from=downloads /tmdedicated /tmdedicated
COPY --from=downloads /usr/bin/nconvert /usr/bin/nconvert
COPY --from=build /app/.local ./.local/
COPY cli.py ./cli
COPY helpers ./helpers/
COPY screens ./screens/

CMD ["./start.sh"]
