#!/bin/bash

docker build --target qas -t marmotcai/shorttrading -f ./Dockerfile .

docker run --rm -ti marmotcai/shorttrading /bin/bash

# docker rm -f my-shorttrading

