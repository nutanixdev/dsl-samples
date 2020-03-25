#!/bin/sh

# install, start and enable nginx
sudo yum -y install epel-release
sudo yum -y install nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# install php 7.2
sudo yum -y install http://rpms.remirepo.net/enterprise/remi-release-7.rpm
sudo yum -y install yum-utils
sudo yum-config-manager --enable remi-php72
sudo yum -y update
sudo yum -y install php72
sudo yum -y install php72-php-fpm php72-php-gd php72-php-json php72-php-mbstring php72-php-mysqlnd php72-php-xml php72-php-xmlrpc php72-php-opcache php72-php-zip

# sort out the php executable
sudo ln -s /usr/bin/php72 /usr/bin/php

# start and enable php72-fpm
sudo systemctl enable php72-php-fpm.service
sudo systemctl start php72-php-fpm.service