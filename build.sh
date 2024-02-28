#!/usr/bin/env bash

set -o errexit  # exit on error

pip3 install -r requirements.txt

python3.11 manage.py collectstatic --no-input
python3.11 manage.py migrate
python3.11 manage.py migrate
spawn "python3.11 manage.py flush"
expect "Are you sure you want to do this?"
send "yes"
expect eof
python3.11 populate_catalog.py
python3.11 manage.py createsuperuser 
