FROM ubuntu:16.04

MAINTAINER AminHP

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
	build-essential openssl libssl-dev \
	python python-pip python-dev \
	libcurl4-nss-dev \
	supervisor docker.io

#RUN useradd cel

RUN pip install --upgrade pip
RUN pip install uwsgi
RUN pip install virtualenv

ENV HOSTPATH /var/www/ijust
ENV DIRPATH /ijust

RUN mkdir -p $HOSTPATH
RUN mkdir -p $DIRPATH
COPY ./deploy/supervisor.conf /etc/supervisor/conf.d/
COPY ./deploy/uwsgi.ini $DIRPATH/uwsgi.ini
COPY ./deploy/start.sh $DIRPATH/start.sh
COPY ./requirements $DIRPATH/requirements

WORKDIR $DIRPATH
RUN virtualenv venv
RUN venv/bin/pip install -r requirements

RUN update-rc.d supervisor defaults
RUN update-rc.d supervisor enable

EXPOSE 6379 27017

CMD ["/bin/bash", "start.sh"]
