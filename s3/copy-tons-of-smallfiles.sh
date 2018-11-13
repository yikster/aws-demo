#!/bin/bash
## USE DEFAULT AWS CREDENTIAL
aws configure set default.s3.max_concurrent_requests 20
aws configure set default.s3.max_queue_size 100000
aws configure set default.s3.multipart_threshold 64MB
aws configure set default.s3.multipart_chunksize 16MB
aws configure set default.s3.max_bandwidth 50MB/s

SRC_ROOT_DIR=srcdir
BUCKET=target_bucket
PREFIX=prefix
time { find $SRC_ROOT_DIR -mindepth 4 -maxdepth 4 -type d -print0 | xargs -n 1 -0 -P 80 -I {} echo 'aws s3 cp --quiet --recursive {} s3://${BUCKET}/${PREFIX}/{} ' ; } 2> copytest/list.txt &
