FROM python:3.14-rc-slim-bookworm
LABEL maintainer="antonbliznuk71@gmail.com"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

COPY . .
