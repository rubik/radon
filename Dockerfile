FROM alpine:edge
MAINTAINER rubik

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN apk --update add \
  python2 python3 py2-pip && \
  pip2 install --upgrade pip && \
  pip2 install --requirement requirements.txt && \
  pip2 install . && \
  mv /usr/bin/radon /usr/bin/radon2 && \
  pip3 install --requirement requirements.txt && \
  pip3 install . && \
  mv /usr/bin/radon /usr/bin/radon3 && \
  rm /var/cache/apk/*

RUN adduser -u 9000 app -D
USER app

WORKDIR /code

VOLUME /code

CMD ["/usr/src/app/codeclimate-radon"]
