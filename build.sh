#!/bin/bash


docker build --target python-builder -t marmotcai/python-app -f ./Dockerfile .

docker rm -f my-st
docker run -p 80:5588 --name my-st -d marmotcai/python-app
