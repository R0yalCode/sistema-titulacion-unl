#!/bin/sh
set -e

cd "$(dirname "$(readlink -f "$0")")"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn --config ./gunicorn.conf.py config.wsgi:application
