#!/usr/bin/env bash
cd ~/vota/
python manage.py compilescss
python manage.py collectstatic --noinput
sh /home/ec2-user/restart.sh
