# configure some best-practice nginx settings

#################################################
#                                               #
# THESE ARE GENERAL SETTINGS ONLY AND WILL NEED #
# NEED TO BE CAREFULLY CHECKED BEFORE USE IN A  #
# PRODUCTION ENVIRONMENT!                       #
#                                               #
# SERIOUSLY, CHECK THEM!  :)                    #
#                                               #
#################################################

# set the number of nginx worker processes to be the same as the number of cores in this system
PROCS=`sudo grep processor /proc/cpuinfo | wc -l`
sudo sed -i -- "s/worker_processes.*/worker_processes $PROCS;/" /etc/nginx/nginx.conf

# set the number of worker connections to the max allowed by nginx
# this allows the server to operate at max potential, if required
sudo sed -i -- 's/worker_connections.*/worker_connections 1024;/' /etc/nginx/nginx.conf

# enable gzip compression
echo "gzip on;
gzip_proxied any;
gzip_types text/plain text/xml text/css application/x-javascript;
gzip_vary on;
gzip_disable \"MSIE [1-6]\.(?!.*SV1)\";" | sudo tee /etc/nginx/conf.d/gzip.conf

# setup cache expiry for static files
echo "location ~*  \.(jpg|jpeg|png|gif|ico|css|js)\$ {
   expires @@{STATIC_EXPIRATION_DAYS}@@d;
}" | sudo tee /etc/nginx/default.d/expires.conf

# disable nginx access logging, if specified at blueprint launch
if [ @@{ENABLE_ACCESS_LOG}@@ == "no" ]
then
	sudo sed -i -- 's/access_log.*/access_log off;/' /etc/nginx/nginx.conf
fi

# set the client buffers
# this is critical on busy systems
echo "client_body_buffer_size  1K;
client_header_buffer_size 1k;
client_max_body_size 1k;
large_client_header_buffers 2 1k;" | sudo tee /etc/nginx/conf.d/buffer.conf

# set the client timeouts - performance improvement under certain circumstances
echo "client_body_timeout 12;
client_header_timeout 12;
send_timeout 10;" | sudo tee /etc/nginx/conf.d/timeout.conf

# set the keepalive timeout separately
# done this way because the above settings are not in nginx.conf by default, but keepalive_timeout is
# this means we can modify it, rather than setting a new value
sudo sed -i -- 's/keepalive_timeout.*/keepalive_timeout 15;/' /etc/nginx/nginx.conf