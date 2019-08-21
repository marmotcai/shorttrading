#!/bin/bash

docker build --target builder -t marmotcai/shorttrading -f ./Dockerfile .

docker run --rm -ti -v $PWD:/root/shorttrading marmotcai/shorttrading /bin/bash

# docker rm -f my-shorttrading

