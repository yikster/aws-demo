#!/bin/bash
if [ $# -ne 2 ]
  then
    echo "Usages: ./deploy.sh ap-northeast-1 ServiceName"
    exit 1
fi

aws cloudformation create-stack --stack-name $2 --template-body file://serverless-pipeline.yaml --region $1 --capabilities CAPABILITY_IAM --parameters ParameterKey=ServiceName,ParameterValue=$2
