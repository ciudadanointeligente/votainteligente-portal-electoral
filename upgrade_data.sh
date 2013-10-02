#!/bin/bash

set -e
#FOR VOTAI

export VOTAINTELIGENTE_DB_NAME=votainteligente.db;


if [ -e $VOTAINTELIGENTE_DB_NAME ]; then mv $VOTAINTELIGENTE_DB_NAME vi_backup.db; fi

python manage.py syncdb --noinput;
python manage.py migrate;
python manage.py loaddata example_data.yaml;


#for candidator
export CANDIDATOR_DB_NAME=development.db;
export CANDIDATOR_DIR=candidator;
export CANDIDATOR_VIRTUALENV=candidator-for-testing;

cd $CANDIDATOR_DIR;

if [ -e $CANDIDATOR_DB_NAME ]; then mv $CANDIDATOR_DB_NAME vi_backup.db; fi

source $CANDIDATOR_VIRTUALENV/bin/activate;
python manage.py syncdb --noinput;
python manage.py loaddata ../candidator_example_data.yaml;

cd ..

#for WRITEIT
export WRITEIT_DB_NAME=writeit.db;
export WRITEIT_DIR=writeit-for-testing;
export WRITEIT_VIRTUALENV=writeit-for-testing;

cd $WRITEIT_DIR;

if [ -e $WRITEIT_DB_NAME ]; then mv $WRITEIT_DB_NAME vi_backup.db; fi

source $WRITEIT_VIRTUALENV/bin/activate;
python manage.py syncdb --noinput;
python manage.py migrate;
python manage.py loaddata ../writeit-example-data.yaml;

cd ..