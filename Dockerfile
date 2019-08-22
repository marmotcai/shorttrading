FROM python:3 AS env

MAINTAINER marmotcai "marmotcai@163.com"

RUN pip install --upgrade pip

ENV WORK_DIR=/root
WORKDIR $WORK_DIR

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

########################################################

FROM env AS app

RUN sed -i '$a\alias ll=\"ls -alF\"' ~/.bashrc
RUN sed -i '$a\alias la=\"ls -A\"' ~/.bashrc
RUN sed -i '$a\alias l=\"ls -CF\"' ~/.bashrc

ENV APP_PATH ${WORK_DIR}/app
ENV PATH $PATH:$APP_PATH

# COPY . .
# CMD [ "python", "./training.py", "-h" ]

