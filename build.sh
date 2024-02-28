#!/usr/bin/env bash

set -o errexit  # exit on error

pip3 install -r requirements.txt

python3.11 manage.py collectstatic --no-input
python3.11 manage.py migrate
export DJANGO_SUPERUSER_EMAIL=alumnodb@alumnodb.com
export DJANGO_SUPERUSER_USERNAME=alumnodb
export DJANGO_SUPERUSER_PASSWORD=alumnodb 
python3.11 manage.py createsuperuser --no-input
