#!/bin/bash
aws cloudformation create-stack --stack-name $1 --region $2 \
    --profile $3 --template-body file://ec2nat-failover.yml \
    --parameters ParameterKey=PAZ1NatInstanceId,ParameterValue=$4 ParameterKey=PAZ2NatInstanceId,ParameterValue=$5 ParameterKey=PAZ1RouteTableId,ParameterValue=$6 ParameterKey=PAZ2RouteTableId,ParameterValue=$7 ParameterKey=PCheckInterval,ParameterValue=$8 \
    --capabilities CAPABILITY_IAM --disable-rollback	\
