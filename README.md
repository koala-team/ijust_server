# IJust

IJust is an open-source judge system used for ACM contests. Basically, it's  an API server which provides you with all the essential features a judge system demands. The main goal was to implement a secure judge system for *Iran University of Science and Technology* (**IUST**).

Implementation was done using *Python*, *Docker* and *Bash*. 


## Getting Started


### Prerequisites

    $ sudo apt-get install mongodb-server redis-server openssl libssl-dev curl libcurl4-nss-dev python-pip
    $ sudo pip install virtualenv
    $ sudo apt-get install docker docker.io docker-compose
    $ docker build -f project/modules/ijudge/Dockerfile -t ijudge project/modules/ijudge/

### Running the Server

The following commands ought to be written and run on separate shells.

    $ python manager.py celery
    $ python manager.py run

### Testing

These commands need to be written and run on separate shells as well.

    $ python manager.py testing

The above line, makes the server run on the testing mode.

    $ python manager.py test

And this line, runs the test cases.

### Deployment

With the use of *Docker* and *NGINX*, the script mentioned below deploys APIServer.
    
	$ sudo -i
    $ ./install.sh

It is suggested that you reboot your system afterwards.

You can also adjust your deployment configurations in the *project/conf.py* file.

After running the above commands, if you add the following line of code to your *project/conf.py* file, you can view your errors' description:

    DEBUG = True

Using [google reCAPTCHA admin](https://www.google.com/recaptcha/admin) you can use your own reCAPTCHA keys. The reCAPTCHA can also be disabled.

    RECAPTCHA_ENABLED = True
    RECAPTCHA_SITE_KEY = "6LeDPwcTAAAAADVt4vp-kdTHXcbl76JbRFK3PUV5"
    RECAPTCHA_SECRET_KEY = "6LeDPwcTAAAAAKF5mXqJpKqo1NW2nntCrjyFwi3Q"
 
For this project to work properly, you need to change our default domains ([acm.iust.ac.ir](https://acm.iust.ac.ir/), [ijust.ir](https://ijust.ir/), [www.ijust.ir](https://www.ijust.ir/)) in the following files:

>install.sh
>
>deploy/nginx.conf

It is to be noted that, HTTPS is the default server protocol. However, you can run your server on HTTP by changing configurations in the two files mentioned above.

### APIdoc

After running the sever, you Are able to view Flasgger's Apidoc in the following link:

>[http://localhost:8080/apidocs/index.html](http://localhost:8080/apidocs/index.html)


## Usage


### Test Case Format

You need to create a zip folder for each group of test cases provided for a question, containing two folders: inputs and outputs. Place your input and output files respectively in each. Make sure the files have the exact same name.

    - inputs/
	    - 1
	    - 2    
    - outputs/
	    - 1
	    - 2


## Features


- **Sandboxing:** With the use of a *Docker*, we were able to isolate our systems, so that the web service and users' codes run in different containers, Which the latter can only access input test cases and the submitted code.

- **Adding new language:** The *Docker* image used for submitting user codes is designed in a way that a new programming language can easily be added to it.

- **RESTful API:** It has been properly documented using [Flasgger](https://github.com/rochacbruno/flasgger).

- **Auto virtualenv:** The system’s *virtualenv* is automatically controlled and there is no need for users to set up or activate its own virtual environment each time.

- **Easy Deployment:** Fast & easy deployment using **uWSGI**, **NGINX** and **Docker**.

- **ijudge:** The [ijudge module](https://github.com/k04la/ijust_server/tree/master/project/modules/ijudge) which handles sandboxing, compiling and running codes, can be used independently in other projects and contexts. Therefore, if you don’t need a web server and only want to run your codes in an isolated environment, this module is your answer.


## Contribution


Due to short timing, we weren't able to implement some of the features we had in mind. Including:

- **Testing:** we weren’t able to provide a test plan and test cases. But the current code has been tested in some contests and there is a 99% chance that it works correctly and is bug-free.

- **Authorization:** We have no framework for static and dynamic authorization, and currently they are hard coded.

- **Supported Languages:** The project supports a few programming languages, but new ones can easily be added.

- **Notification System:** The project lacks a notification system, for notifying users whether their code has been accepted or not, who wants to join a contest, and etc. .

in addition to above features, share your ideas with us about what features might improve the quality of the project.

*Feel free to contribute ! :)*
 