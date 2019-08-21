FROM python AS builder

MAINTAINER marmotcai "marmotcai@163.com"

RUN pip install --upgrade pip
RUN pip install tensorflow
# RUN pip install --pre jupyter-tensorboard
# RUN pip install tensorlayer
RUN pip install keras
RUN pip install nltk
RUN pip install pandas
RUN pip install tushare
RUN pip install matplotlib
RUN pip install plotly
RUN pip install arrow
RUN pip install tflearn

USER $NB_USER
# USER root
# RUN chown jovyan.users data -R

FROM builder as qas

ENV WORK_DIR=/root
WORKDIR ${WORK_DIR}

ENV APP_NAME=shorttrading
ENV GIT_URL=https://marmotcai:aa!112233@github.com/marmotcai/shorttrading.git
RUN git clone $GIT_URL

ENV WORK_DIR=${WORK_DIR}/${APP_NAME}
WORKDIR $WORK_DIR

RUN pip install -r requirements.txt

CMD ["python3", "./training.py -h"]

