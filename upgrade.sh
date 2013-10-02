#!/bin/bash
set -e
export DB_NAME="votainteligente.db"

pip install -r requirements.txt
python manage.py migrate

./start_local_popit_api.bash
./start_local_writeit.bash
./start_local_candidator.bash


python manage.py runserver
