#!/bin/sh

# make sure PHP is installed, first
command -v php >/dev/null 2>&1 || { echo >&2 "This script requires php but it isn't installed or isn't in your PATH.  Aborting."; exit 1; }
command -v wget >/dev/null 2>&1 || { echo >&2 "This script requires wget but it isn't installed or isn't in your PATH.  Aborting."; exit 1; }

# download and install composer
# note this script installs composer locally at this point
EXPECTED_SIGNATURE=$(wget -q -O - https://composer.github.io/installer.sig)
php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
ACTUAL_SIGNATURE=$(php -r "echo hash_file('SHA384', 'composer-setup.php');")

if [ "$EXPECTED_SIGNATURE" != "$ACTUAL_SIGNATURE" ]
then
    >&2 echo 'ERROR: Invalid installer signature'
    rm composer-setup.php
    exit 1
fi

php composer-setup.php --quiet
RESULT=$?
rm composer-setup.php
#exit $RESULT

# install composer globally
sudo mv "/home/`whoami`/composer.phar" /usr/local/bin/composer

exit $RESULT