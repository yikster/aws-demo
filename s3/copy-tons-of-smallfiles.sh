#!/bin/bash
SRC_ROOT_DIR=srcdir
BUCKET=target_bucket
PREFIX=prefix
time { find $SRC_ROOT_DIR -mindepth 4 -maxdepth 4 -type d -print0 | xargs -n 1 -0 -P 80 -I {} echo 'aws cp --recursive {} s3://${BUCKET}/${PREFIX}/{} ' ; } 2> copytest/list.txt &
