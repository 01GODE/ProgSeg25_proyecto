# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY ./app /app

RUN apt-get update && apt-get install -y coreutils default-libmysqlclient-dev gcc gawk grep iputils-ping openssh-client pkg-config sshpass && rm -rf /var/lib/apt/lists/* && pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 debian
USER debian

CMD ["gunicorn", "proyecto.wsgi:application", "--bind", "0.0.0.0:8000"]
