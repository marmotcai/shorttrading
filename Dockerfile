FROM python AS builder

MAINTAINER marmotcai "marmotcai@163.com"

RUN sed -i '$a\alias ll=\"ls -alF\"' ~/.bashrc
RUN sed -i '$a\alias la=\"ls -A\"' ~/.bashrc
RUN sed -i '$a\alias l=\"ls -CF\"' ~/.bashrc

RUN pip install --upgrade pip

# RUN pip install tensorflow
# RUN pip install tensorlayer
# RUN pip install keras
# RUN pip install nltk
# RUN pip install pandas
# RUN pip install tushare
# RUN pip install matplotlib
# RUN pip install plotly
# RUN pip install arrow
# RUN pip install tflearn

# RUN pip install --pre jupyter-tensorboard
# USER $NB_USER
# USER root
# RUN chown jovyan.users data -R

FROM builder as qas

ENV APP_NAME=shorttrading
ENV GIT_URL=https://marmotcai:aa!112233@github.com/marmotcai/shorttrading.git

ENV WORK_DIR=/root/${APP_NAME}

RUN mkdir -p $WORK_DIR
COPY ./ $WORK_DIR
# RUN git clone $GIT_URL

WORKDIR $WORK_DIR

RUN pip freeze > requirements.txt
RUN pip install -r requirements.txt

CMD ["python3", "./training.py -h"]

