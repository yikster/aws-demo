#!/bin/bash
## This is tested on AmazonLinux
## Check your python version
## sudo yum install python36-devel

sudo pip-3.6 install bzt
bzt quick_test.yml
