FROM python:slim-trixie

RUN DEBIAN_FRONTEND=noninteractive apt-get install --update --no-install-recommends -y ffmpeg

ARG VERSION

RUN python3 -m pip install -U recitale==$VERSION

RUN mkdir /var/www/

WORKDIR /var/www/

ENTRYPOINT ["recitale"]
