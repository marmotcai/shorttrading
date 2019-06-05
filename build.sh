#!/bin/bash


docker build --target python-builder -t marmotcai/shorttrading -f ./Dockerfile .

docker rm -f my-shorttrading
docker run -p 80:5588 --name my-shorttrading -d marmotcai/shorttrading

# docker run --rm -ti marmotcai/shorttrading /bin/bash
