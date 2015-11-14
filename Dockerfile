FROM python:3.5
MAINTAINER Rubik

WORKDIR /usr/src/app

COPY tox_requirements.txt /usr/src/app/
RUN pip install -r tox_requirements.txt

RUN adduser -u 9000 app
COPY . /usr/src/app
RUN pip install .

WORKDIR /code

USER app

VOLUME /code

CMD ["/usr/src/app/codeclimate-radon"]
