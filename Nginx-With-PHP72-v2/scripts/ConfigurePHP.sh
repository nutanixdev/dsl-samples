#!/bin/sh

# tell the webserver how to process requests for .php files
# in this case, we're passing the request to PHP-FPM
echo "## enable php support ##
location ~ \.php$ {
	root /usr/share/nginx/html;
	fastcgi_pass   127.0.0.1:9000;
	fastcgi_index  index.php;
	include        fastcgi_params;
	fastcgi_param  SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
}" | sudo tee /etc/nginx/default.d/php72.conf

# set the default document for the default site
echo "# set the site's default document
index index.php;" | sudo tee /etc/nginx/default.d/index.conf

# causes the php interpreter to only try the literal path given and to stop processing if the file is not found
# from https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/
sudo sed -i -- 's/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/' /etc/opt/remi/php72/php.ini
sudo sed -i -- 's/;security.limit_extensions = .*/security.limit_extensions = \.php \.php3 \.php4 \.php5 \.php7/' /etc/opt/remi/php72/php-fpm.d/www.conf

# restart the services that are affected by our configuration changes
sudo systemctl restart nginx
sudo systemctl restart php72-php-fpm.service