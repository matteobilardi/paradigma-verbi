#!/bin/bash

sudo service nginx restart
source ../env/bin/activate
sudo redis-server ./database/redis.conf dir $PWD/.. &
python3.6 run.py
