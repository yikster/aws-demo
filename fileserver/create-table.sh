#!/bin/bash
PROFILE=$1
REGION=$2

aws dynamodb create-table --profile $PROFILE --region $REGION\
    --table-name=FileInfo \
    --attribute-definitions \
        AttributeName=guid,AttributeType=S \
        AttributeName=createdAt,AttributeType=N \
    --key-schema \
        AttributeName=guid,KeyType=HASH \
        AttributeName=createdAt,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5