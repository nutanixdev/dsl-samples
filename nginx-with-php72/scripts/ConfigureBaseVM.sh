#!/bin/sh

# update centos packages
sudo yum -y update

# install some useful packages
sudo yum -y install git bash-completion vim net-tools bind-utils wget firewalld

# set the hostname
sudo hostnamectl set-hostname @@{HOSTNAME}@@