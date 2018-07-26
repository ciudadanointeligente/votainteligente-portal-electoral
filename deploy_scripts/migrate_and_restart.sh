#!/usr/bin/env bash
cd ~/vota/
python manage.py  migrate
sh /home/ec2-user/restart.sh
