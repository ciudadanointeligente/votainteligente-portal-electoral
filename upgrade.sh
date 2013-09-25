#!/bin/bash
set -e
export DB_NAME="votainteligente.db"

if [ -e $DB_NAME ]; then mv $DB_NAME vi_backup.db; fi
pip install -r requirements.txt
python manage.py syncdb --noinput
python manage.py migrate
python manage.py loaddata example_data.yaml


./start_local_popit_api.bash
./start_local_writeit.bash
