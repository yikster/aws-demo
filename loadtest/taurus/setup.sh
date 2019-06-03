#!/bin/bash
## This is tested on AmazonLinux
## Check your python version
sudo yum -y remove java-1.7.0
sudo yum -y install java-1.8.0
sudo yum install -y python3-devel.x86_64
sudo yum install -y gcc
sudo pip3 install bzt
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
bzt quick_test.yml
