FROM marmotcai/centos-base AS python
MAINTAINER marmotcai "marmotcai@163.com"

ENV WORK_DIR=/root

RUN yum clean all && \
        yum makecache fast

RUN yum install -y gcc gcc-c++ make zlib zlib-devel libffi-devel openssl-devel

# ENV OPENSSL_URL=https://www.openssl.org/source/openssl-1.0.2s.tar.gz
# ENV OPENSSL_SRC=$WORK_DIR/openssl-1.0.2s

# RUN wget -O ${WORK_DIR}/openssl.tar.gz ${OPENSSL_URL} && \
#     tar -zxvf ${WORK_DIR}/openssl.tar.gz -C ${WORK_DIR}

# RUN cd ${OPENSSL_SRC} && \
#     ./config --prefix=/usr/local/openssl no-zlib && \
#     make && \
#     make install

# RUN mv /usr/bin/openssl /usr/bin/openssl.bak && \
#    mv /usr/include/openssl/ /usr/include/openssl.bak

# RUN ln -s /usr/local/openssl/include/openssl /usr/include/openssl && \
#     ln -s /usr/local/openssl/lib/libssl.so.1.1 /usr/local/lib64/libssl.so && \
#     ln -s /usr/local/openssl/bin/openssl /usr/bin/openssl


# RUN echo "/usr/local/openssl/lib" >> /etc/ld.so.conf && \
#     ldconfig -v

# RUN openssl version

###################################################################################################

ENV PYTHON_URL=https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
ENV PYTHON_SRC=$WORK_DIR/Python-3.7.4

RUN wget -O ${WORK_DIR}/python.tgz ${PYTHON_URL} && \
    tar -zxvf ${WORK_DIR}/python.tgz -C ${WORK_DIR}

RUN cd ${PYTHON_SRC} && \
    ./configure --prefix=/usr/local/python3 && \
    make && \
    make install

RUN ln -s /usr/local/python3/bin/python3.7 /usr/bin/python3
RUN ln -s /usr/local/python3/bin/pip3.7 /usr/bin/pip3

RUN pip3 install --upgrade pip
RUN python3 --version

###################################################################################################

FROM python AS builder

MAINTAINER marmotcai "marmotcai@163.com"

ENV APP_NAME=shorttrading
ENV GIT_URL=https://xxxxxx:xxxxxx@github.com/marmotcai/shorttrading.git

ENV WORK_DIR=/root/${APP_NAME}

RUN mkdir -p $WORK_DIR
COPY ./ $WORK_DIR
# RUN git clone $GIT_URL

WORKDIR $WORK_DIR

RUN pip3 freeze > requirements.txt
RUN pip3 install -r requirements.txt

CMD ["python3", "./training.py -h"]

