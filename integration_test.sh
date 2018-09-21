#!/bin/bash

trap "trap - SIGTERM && kill -- -$$ && rm -rf ./examples/abcd" SIGINT SIGTERM EXIT

DATADIR_R=/home/jacek/golem_data/data21_r
DATADIR_P=/home/jacek/golem_data/data12_p

pkill redis-server > /dev/null

redis-server > /dev/null 2>&1 &
redis-cli flushall > /dev/null 2>&1

set -e


cd ~/golem_orig/

/home/jacek/golemenv/bin/python3 golemapp.py --log-level INFO --datadir $DATADIR_R --accept-terms --protocol_id 97 --password "k123@" -p localhost:40103 -r localhost:61000 --concent disabled > /dev/null &

sleep 3

/home/jacek/golemenv/bin/python3 golemapp.py --log-level INFO --datadir $DATADIR_P --accept-terms --protocol_id 97 --password "k123@" -p localhost:40102 -r localhost:61001 --concent disabled > /dev/null &

sleep 3

cd ~/golem_remote/

sleep 18


PYTHON_PATH=/home/jacek/anaconda3/bin/python3
$PYTHON_PATH examples/iteration7_task_files.py

echo "Done"
