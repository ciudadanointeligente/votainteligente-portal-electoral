#!/bin/bash
set -e
coverage run manage.py test elections
coverage report -m
