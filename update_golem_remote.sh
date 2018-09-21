#!/bin/bash

cd golem_remote
git add .
git commit -am "Update"
git push

/home/jacek/golemenv/bin/pip install --upgrade git+https://github.com/golemfactory/golem-remote.git
/home/jacek/anaconda3/bin/pip install --upgrade git+https://github.com/golemfactory/golem-remote.git

cd /home/jacek/golem_orig/apps/runf/resources/images/
export DOCKER_ID_USER="golemfactory"        

sed -i 's/VERSION=1/VERSION=11/g' Dockerfile

docker build . -t $DOCKER_ID_USER/runf
