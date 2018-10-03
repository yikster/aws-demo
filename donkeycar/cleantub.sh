#!/bin/bash
TUB_PATH="tub/"
ls -al $TUB_PATH | wc -l
for i in {6800..8000}; do rm $TUB_PATH/${i}_cam-image_array_.jpg; rm $TUB_PATH/record_${i}.json; done
ls -al $TUB_PATH | wc -l
