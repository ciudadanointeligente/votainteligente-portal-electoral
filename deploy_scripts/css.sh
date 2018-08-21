#!/usr/bin/env bash
cd ~/vota/
nohup python manage.py compilescss &
nohup python manage.py collectstatic --noinput --clear &
