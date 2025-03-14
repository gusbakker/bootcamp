FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libffi-dev \
    gettext \
    postgresql-client \
    bash

# Upgrade pip
RUN pip install --upgrade pip

# Requirements are installed here to take advantage of caching
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

# Copy entrypoint and start scripts
COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
COPY ./compose/local/django/start.sh /start.sh

# Fix line endings and make scripts executable
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN sed -i 's/\r//' /start.sh
RUN chmod +x /start.sh

WORKDIR /app

ENTRYPOINT ["bash", "/entrypoint.sh"] # Use bash for pipefail