from python:slim-bookworm

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y ffmpeg

ARG VERSION

RUN python3 -m pip install -U recitale==$VERSION

RUN mkdir /var/www/

WORKDIR /var/www/

ENTRYPOINT ["recitale"]
