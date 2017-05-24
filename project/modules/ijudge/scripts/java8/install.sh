#! /bin/bash

apt-get install -y software-properties-common default-jre default-jdk
add-apt-repository ppa:webupd8team/java
apt-get update && \
	echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
	apt-get install -y oracle-java8-installer
