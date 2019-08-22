#!/bin/bash

APP_NAME=shorttrading

cmd=${1}
param=${2}
param1=${3}

case $cmd in
  image)
    if [ ! -z "${param}" ];then
      docker build --target ${param} -t marmotcai/${param} -f ./Dockerfile .
    else
      docker build -t marmotcai/${APP_NAME} -f ./Dockerfile .
    fi 
  ;;

  bash)
    docker run --rm -ti -v $PWD:/root/app marmotcai/shorttrading /bin/bash
  ;;

  python)
    docker run --rm -ti -v $PWD:/root/app marmotcai/shorttrading python /root/app/${param} ${param1}
  ;; 

  *)
    echo "use: sh build.sh image"
    echo "use: sh build.sh bash"
    echo "use: sh build.sh python training.py -v"
  ;;
esac

exit 0;

# docker rm -f my-shorttrading
# docker run --name my-shorttrading -ti -d -p 3222:22 -v $PWD:/root/shorttrading marmotcai/shorttrading
