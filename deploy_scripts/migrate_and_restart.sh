#!/usr/bin/env bash
source ~/.virtualenvs/vota/bin/activate
cd ~/vota/
python manage.py compilescss
python manage.py collectstatic --noinput
