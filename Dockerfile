# syntax=docker/dockerfile:1
FROM python:3.11-slim

RUN apt-get update && apt-get install -y tesseract-ocr-all \
    python3-pip \
    python3-opencv \
    ffmpeg \
    libsm6 \
    libxext6 \
    gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip && pip install -U requirementslib

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/trainerdex

COPY Pipfile Pipfile
RUN python -c 'from requirementslib.models.pipfile import Pipfile; pf = Pipfile.load("."); pkgs = [pf.requirements]; print("\n".join([pkg.as_line() for section in pkgs for pkg in section]))' > requirements.txt
RUN pip install -r requirements.txt

COPY . .
