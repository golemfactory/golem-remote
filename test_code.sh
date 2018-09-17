#!/bin/bash

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
pkill redis-server > /dev/null
redis-server > /dev/null 2>&1 &

set -e

echo "Formatting code"
yapf golem_remote -r -i --style ./.style.yapf 


echo "Testing with pytest"
pytest .

echo "Testing with pylint"
pylint golem_remote

echo "Testing with mypy"
mypy . --ignore-missing-imports

echo "OK"
