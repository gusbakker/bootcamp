#!/bin/sh

set -o errexit
#set -o pipefail
set -o nounset
set -o xtrace


python manage.py migrate
python manage.py collectstatic --noinput
#python manage.py runserver 0.0.0.0:8000
daphne config.asgi:application --port 8000 --bind 0.0.0.0 -v2
