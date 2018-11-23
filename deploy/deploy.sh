#! /bin/sh

# docker build -f Dockerfile -t ijust ../
# docker build -f ../project/modules/ijudge/Dockerfile -t ijudge ../project/modules/ijudge/

docker pull salarn14/ijust:latest
docker pull salarn14/ijudge:latest
docker tag salarn14/ijust:latest ijust:latest
docker tag salarn14/ijudge:latest ijudge:latest

docker-compose up -d
