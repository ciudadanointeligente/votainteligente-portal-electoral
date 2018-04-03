#!/usr/bin/env bash
source ~/.virtualenvs/merepresenta/bin/activate
python manage.py  migrate
sudo supervisorctl restart merepresenta
python manage.py compilescss
python manage.py collectstatic --noinput
