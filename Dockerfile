FROM alpine:edge
LABEL maintainer="rubik"

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN apk --update add \
  python3 py3-pip && \
  pip3 install --requirement requirements.txt && \
  pip3 install . && \
  mv /usr/bin/radon /usr/bin/radon3 && \
  rm /var/cache/apk/*

RUN adduser -u 9000 app -D
USER app

WORKDIR /code

VOLUME /code

CMD ["/usr/src/app/codeclimate-radon"]
