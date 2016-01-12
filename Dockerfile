FROM python:3.5.1-slim
MAINTAINER rubik

WORKDIR /usr/src/app

RUN apt-get update && \
  apt-get install -y python2.7 python-pip && \
  apt-get clean

COPY tox_requirements.txt /usr/src/app/
RUN pip install --quiet --requirement tox_requirements.txt
RUN pip2 install --quiet --requirement tox_requirements.txt

RUN adduser -u 9000 app

COPY . /usr/src/app
RUN pip install --quiet . && \
  mv /usr/local/bin/radon /usr/local/bin/radon3
RUN pip2 install --quiet . && \
  mv /usr/local/bin/radon /usr/local/bin/radon2

WORKDIR /code

USER app

VOLUME /code

CMD ["/usr/src/app/codeclimate-radon"]
