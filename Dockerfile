# syntax=docker/dockerfile:1
FROM python:3.10-slim

RUN pip install -U pipenv virtualenv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/trainerdex

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv sync

COPY . .

RUN pipenv run python manage.py migrate --no-color --noinput -v 3

RUN pipenv run gunicorn --worker-tmp-dir /dev/shm config.wsgi