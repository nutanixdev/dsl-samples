#!/bin/sh

# configure the firewall to allow HTTP requests (port 80, by default)
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload