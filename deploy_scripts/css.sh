#!/usr/bin/env bash
cd ~/vota/
python manage.py  migrate
sudo supervisorctl restart merepresenta
python manage.py compilescss
python manage.py collectstatic --noinput
