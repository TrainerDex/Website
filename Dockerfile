# syntax=docker/dockerfile:1
FROM python:3.10-slim

RUN apt-get update 
RUN apt-get install -y tesseract-ocr-all
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-opencv
RUN apt-get install -y ffmpeg
RUN apt-get install -y libsm6
RUN apt-get install -y libxext6
RUN apt-get install -y gettext

RUN pip install -U pipenv virtualenv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/trainerdex

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv sync

COPY . .
