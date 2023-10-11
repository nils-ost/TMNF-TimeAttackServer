FROM ubuntu:22.04 AS dedicated

ENV USER root
ENV HOME /tmdedicated
ENV FILE http://files2.trackmaniaforever.com/TrackmaniaServer_2011-02-21.zip

WORKDIR $HOME

RUN apt update \
 && apt install -y --no-install-recommends ca-certificates curl unzip

RUN curl $FILE --output archive.zip --silent \
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
 && apt install -y liblzo2-2 imagemagick \
 && rm -rf /var/cache/apt

COPY --from=dedicated /tmdedicated /tmdedicated
COPY --from=build /app/.local ./.local/
COPY cli.py .
COPY helpers ./helpers/
COPY screens ./screens/

CMD ["/tmdedicated/TrackmaniaServer" "/dedicated_cfg=dedicated_cfg.txt" "/game_settings=MatchSettings/active.txt" "/lan" "/nodaemon"]
