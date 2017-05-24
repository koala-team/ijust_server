# IJust Server


### Installation:

```
$ sudo apt-get install mongodb-server redis-server openssl libssl-dev curl libcurl4-nss-dev python-pip
$ sudo pip install virtualenv
$ sudo apt-get install docker docker.io docker-compose
$ docker build -f project/modules/ijudge/Dockerfile -t ijudge project/modules/ijudge/
```

### Run server:
Run these commands in separate shells.


```
$ python manager.py celery
$ python manager.py run
```

### Test api:
Run these commands in separate shells.

```
$ python manager.py testing
$ python manager.py test
```


### Deploy server:

```
$ ./install.sh
```

### Apidoc:

> [http://localhost:8080/apidocs/index.html](http://localhost:8080/apidocs/index.html)

