FROM python:3.9-slim
LABEL maintainer="dennieking87@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app

COPY . .

RUN mkdir -p /files/media

RUN adduser --disabled-password --no-create-home django-user

RUN chown -R django-user /files/media
RUN chmod -R 755 /files/media

USER django-user
