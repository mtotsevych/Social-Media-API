FROM python:3.13-slim

LABEL maintainer="totsevich02@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN mkdir -p /files/media
RUN chown -R django-user /files/media
RUN chmod -R 755 /files/media

COPY . .

USER django-user
