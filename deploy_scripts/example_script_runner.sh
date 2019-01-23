#!/bin/bash
set -e
LOGFILE=/home/user/vota/ellog.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=3
# user/group to run as
USER=user
GROUP=user
cd /home/user/vota/
test -d $LOGDIR || mkdir -p $LOGDIR
/usr/local/bin/gunicorn votainteligente.wsgi -w $NUM_WORKERS \
  --user=$USER --group=$GROUP --log-level=critical \
  --limit-request-field_size 0\
  --timeout 200\
  --bind unix:/tmp/elsocket.sock\
  --log-file=$LOGFILE 2>>$LOGFILE
