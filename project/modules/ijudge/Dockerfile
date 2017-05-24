FROM ubuntu:16.04

MAINTAINER SALAR

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y bc time
RUN useradd restricted_user

RUN mkdir /var/judge

ADD ./main.sh /var/judge
ADD ./language_dependency.sh /var/judge
ADD ./scripts/ /var/judge/scripts/

WORKDIR /var/judge

RUN /bin/bash language_dependency.sh

CMD ["/bin/bash", "main.sh"]
