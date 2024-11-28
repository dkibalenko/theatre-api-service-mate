FROM python:3.9-slim
LABEL maintainer="dennieking87@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app

COPY . .
