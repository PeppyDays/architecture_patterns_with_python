FROM python:3.9-slim-buster

COPY ../requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src
COPY ../src/ /src/

RUN mkdir -p /tests
COPY ../tests/ /tests/

RUN pip install -e /src
WORKDIR /src
