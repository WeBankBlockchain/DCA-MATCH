#!/bin/bash

mkdir -p /data/app/logs/dca-match/
cd /data/app/dca-match
tar xvfz ma_env.tar.gz
source bin/activate
nohup gunicorn --config gunicorn.conf --preload matcher_starter:app >/dev/null &
# nohup python matcher_maintainer_starter.py >/dev/null &
