FROM ubuntu:18.04

LABEL maintainer="stanaya <tanaya.shou@gmail.com>"

RUN apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncurses5-dev libncursesw5-dev libpng-dev
RUN apt-get -y install libtool autoconf automake pkg-config git emacs wget sudo python2.7 libmecab-dev mecab mecab-ipadic mecab-ipadic-utf8 zip unzip swig
RUN wget https://github.com/zeromq/libzmq/releases/download/v4.2.5/zeromq-4.2.5.tar.gz
RUN tar xvzf zeromq-4.2.5.tar.gz
RUN cd zeromq-4.2.5 && \
    ./configure && \
    make && \
    make check && \
    make install && \
    ldconfig && \
    ldconfig -p | grep zmq

# add sudo user
RUN groupadd -g 1000 developer && \
    useradd  -g      developer -G sudo -m -s /bin/bash ubuntu && \
    echo 'ubuntu:ubuntu' | chpasswd

RUN echo 'Defaults visiblepw'             >> /etc/sudoers
RUN echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers


# 以下は ubuntu での操作
USER ubuntu
WORKDIR /home/ubuntu/

RUN git clone https://github.com/stanaya/LightLDA.git --recursive
RUN cd LightLDA/ && \
    sh build.sh

# pyenv
RUN git clone git://github.com/yyuu/pyenv.git .pyenv
RUN git clone https://github.com/yyuu/pyenv-pip-rehash.git ~/.pyenv/plugins/pyenv-pip-rehash
ENV HOME /home/ubuntu
ENV PYENV_ROOT ${HOME}/.pyenv
ENV PATH ${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

RUN echo 'eval "$(pyenv init -)"' >> ~/.bashrc && \
    eval "$(pyenv init -)"

RUN pyenv install anaconda3-5.3.1
RUN pyenv global anaconda3-5.3.1
RUN pip install --upgrade pip
RUN pip install mecab-python3 gensim lightGBM awscli

# mecab-neologd
RUN git clone https://github.com/neologd/mecab-ipadic-neologd.git
RUN cd mecab-ipadic-neologd && \
    sudo bin/install-mecab-ipadic-neologd -y

RUN git clone https://github.com/stanaya/lda_d2c.git
