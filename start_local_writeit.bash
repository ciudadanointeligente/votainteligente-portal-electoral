#!/bin/bash

#I coppied this from our mysociety friends
#https://github.com/mysociety/popit-django/blob/master/start_local_popit_api.bash

set -e

# this script will fetch a copy of the popit-api and start it running locally.
# Assumes that Node is installed, and that MongoDB is running locally and allows
# databases to be created without auth.
#
# This is not a robust way to run the api, it is intended for local dev and for
# testing on Travis.


# just checkout the mysociety-deploy branch
# http://stackoverflow.com/a/7349740/5349
export DIR=writeit-for-testing
export BRANCH=master
export REMOTE_REPO=https://github.com/ciudadanointeligente/write-it.git
export PORT=3001
export VIRTUALENV=writeit-for-testing

if [ ! -e $DIR ]; then mkdir $DIR; fi
cd $DIR;

# If needed clone the repo
if [ ! -e done.txt ]; then
  git init;
  git remote add -t $BRANCH -f origin $REMOTE_REPO;
  git checkout $BRANCH;

  #echo "{ \"serverPort\": $PORT }" > config/general.json

  # install the required node modules
  #npm install pow-mongodb-fixtures --quiet
  #npm install --quiet
  virtualenv $VIRTUALENV
  source $VIRTUALENV/bin/activate
  pip install -r requirements.txt
  python manage.py syncdb --noinput
  python manage.py migrate --noinput
  python manage.py loaddata ../example_data.yaml

  touch done.txt;
else
  git pull origin $BRANCH
  source $VIRTUALENV/bin/activate
  pip install -r requirements.txt
fi



# Run the server in the background. Send access logging to file.
#node server.js > access.log &

# give it a chance to start and then print out the url to it
sleep 2
python manage.py runserver $PORT > writeit_access.log &
echo "API should now be running on http://localhost:$PORT/api"
