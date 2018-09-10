#!/bin/bash

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

pkill redis-server > /dev/null 2>&1

redis-server > /dev/null 2>&1 &
redis-cli flushall > /dev/null 2>&1

set -e

PYTHON_PATH=/home/jacek/golemenv/bin/python3


cd ~/golem_orig/

$PYTHON_PATH golemapp.py --log-level INFO --datadir ~/golem_data/data8_r --accept-terms --protocol_id 97 --password "k123@" -p localhost:40103 -r localhost:61000 > /dev/null 2>&1 &

sleep 3

$PYTHON_PATH golemapp.py --log-level INFO --datadir ~/golem_data/data10_p --accept-terms --protocol_id 97 --password "k123@" -p localhost:40102 -r localhost:61001 > /dev/null 2>&1 &

sleep 3

cd ~/golem_remote/examples

sleep 12

PYTHON_PATH=/home/jacek/anaconda3/bin/python3
$PYTHON_PATH iteration6_golem_remote_package.py
echo "Done"
