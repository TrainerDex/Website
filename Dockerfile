# syntax=docker/dockerfile:1
FROM python:3.10-slim

RUN apt-get update && apt-get install -y tesseract-ocr-all python3-pip
RUN pip install -U pipenv virtualenv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/trainerdex

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv sync

COPY . .
