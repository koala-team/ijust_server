#! /bin/sh

docker build -f Dockerfile -t ijust ../
docker build -f ../project/modules/ijudge/Dockerfile -t ijudge ../project/modules/ijudge/
docker-compose up -d
