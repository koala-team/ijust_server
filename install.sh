#! /bin/sh

apt-get install -y openssl letsencrypt
apt-get install -y docker docker.io docker-compose
apt-get install nginx
apt-get install -y apache2-utils

service nginx stop
service docker stop

mkdir -p /var/www/ijust
cd /var/www/ijust

git clone https://github.com/k04la/ijust_server
mv ijust_server server
mkdir log
touch reload

cd /etc/nginx/sites-enabled
rm default
ln -s /var/www/ijust/server/deploy/nginx.conf ijust
openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
letsencrypt certonly --email=mdan.hagh@gmail.com --agree-tos -d acm.iust.ac.ir -d ijust.ir -d www.ijust.ir

cd /var/www/ijust/server/project
cp conf.py.sample conf.py

cd /var/www
chown www-data:www-data -R ijust

service nginx start # ensure that port 80 and 443 are open
service docker start

htpasswd -c /etc/nginx/.htpasswd AminHP

cd /var/www/ijust/server/deploy
./deploy.sh
