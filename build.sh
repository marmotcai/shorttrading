#!/bin/bash

docker build --target qas -t marmotcai/shorttrading -f ./Dockerfile .

docker rm -f my-shorttrading
docker run --name my-shorttrading -d marmotcai/shorttrading

