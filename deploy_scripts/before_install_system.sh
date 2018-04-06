#!/usr/bin/env bash
sudo yum install redhat-rpm-config git zlib-devel libjpeg-devel GraphicsMagick-c++-devel boost-devel gcc gcc-c++ -y

pip install --user django-storages psycopg2-binary boto3
