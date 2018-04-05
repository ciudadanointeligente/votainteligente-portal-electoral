#!/usr/bin/env bash
source ~/.virtualenvs/merepresenta/bin/activate
cd ~/vota/
python manage.py  migrate
sudo supervisorctl restart merepresenta
python manage.py compilescss
python manage.py collectstatic --noinput
