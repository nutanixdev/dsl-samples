#!/bin/sh

# remove the default files and create a basic index.php file
sudo rm -Rf /usr/share/nginx/html/*

# set permissions, first
# DON'T DO THIS IN PRODUCTION!
sudo chown -R $USER:$USER /usr/share/nginx/html

# create the composer structure
cd /usr/share/nginx/html
composer init --name fakeperson/fakedemo --description "Fake Demo" --author "You <you@you.com>" --no-interaction
composer install

# setup the website contents
echo "<?php
require 'vendor' . DIRECTORY_SEPARATOR . 'autoload.php';
?>
<html>
<head>
   <title>Nginx Site Index</title>
   <link href='https://fonts.googleapis.com/css?family=Droid+Sans:400,700' rel='stylesheet' type='text/css'>
   <style type=\"text/css\">
      body { font-family: 'Droid Sans', sans-serif; }
   </style>
</head>
<body>
   <p>Hello, world ... ;-)</p>
</body>
</html>" | sudo tee /usr/share/nginx/html/index.php