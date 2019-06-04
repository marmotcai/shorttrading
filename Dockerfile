FROM python AS python-builder

MAINTAINER marmotcai "marmotcai@163.com"

RUN apt update && \
    apt install -y vim

RUN sed -i '$a\alias ll=\"ls -alF\"' ~/.bashrc
RUN sed -i '$a\alias la=\"ls -A\"' ~/.bashrc
RUN sed -i '$a\alias l=\"ls -CF\"' ~/.bashrc

ENV WORK_DIR=/root
WORKDIR ${WORK_DIR}

ENV BASE_APP_NAME=easyquotation
ENV BASE_GIT_URL=https://github.com/shidenggui/easyquotation.git

RUN git clone $BASE_GIT_URL

RUN cd $BASE_APP_NAME && \
    python setup.py install

WORKDIR ${WORK_DIR}

ENV APP_NAME=shorttrading
ENV GIT_URL=https://github.com/marmotcai/shorttrading.git

RUN git clone $GIT_URL

ENV WORK_DIR=${WORK_DIR}/${APP_NAME}

EXPOSE 5588

WORKDIR $WORK_DIR

ENTRYPOINT [ "python3.7", "main.py" ]
