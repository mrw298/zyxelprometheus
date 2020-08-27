#!/bin/bash

set -e

docker login --username andrewjw --password $DOCKER_TOKEN

docker build --build-arg VERSION=$TRAVIS_TAG -t andrewjw/zyxelprometheus:$TRAVIS_TAG .

docker push andrewjw/zyxelprometheus:$TRAVIS_TAG
