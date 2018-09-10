#!/bin/bash

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

pkill redis-server > /dev/null

redis-server > /dev/null 2>&1 &
redis-cli flushall > /dev/null 2>&1

set -e


cd ~/golem_orig/

/home/jacek/golemenv/bin/python3 golemapp.py --log-level INFO --datadir ~/golem_data/data8_r --accept-terms --protocol_id 97 --password "k123@" -p localhost:40103 -r localhost:61000 > /dev/null &

sleep 3

/home/jacek/golemenv/bin/python3 golemapp.py --log-level INFO --datadir ~/golem_data/data11_p --accept-terms --protocol_id 97 --password "k123@" -p localhost:40102 -r localhost:61001 > /dev/null &

sleep 3

cd ~/golem_remote/examples

sleep 12

PYTHON_PATH=/home/jacek/anaconda3/bin/python3
$PYTHON_PATH iteration6_golem_remote_package.py
echo "Done"
