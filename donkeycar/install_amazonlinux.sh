#!/bin/bash
#sudo yum install python35
DONKEY_PATH=~/d2
virtualenv ~/env -p python35
source ~/env/bin/activate
pip install tensorflow==1.8.0
pip install donkeycar[tf]
#git clone https://github.com/wroscoe/donkey ~/env/donkeycar
#cd ~/env/donkeycar
python --version
#python35 --version
#pip3 install -e .

donkey createcar $DONKEY_PATH
