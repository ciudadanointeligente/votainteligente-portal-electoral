#!/bin/bash
set -e

sudo apt-get install python-pgmagick 
sudo apt-get install libgraphicsmagick++1-dev 
sudo apt-get install libboost-python-dev
./upgrade.sh
