#!/bin/bash
export AWS_PROFILE=default-ks4

PRD_ACCOUNT_NO=123456789012
ASSUME_ROLE_NAME=STSForDeployProduct
DEV_ACCOUNT_NO=023456789012
REGION=ap-northeast-2
PROJECT_ID=dev-java-ec2

python codepipeline.py $REGION $PROJECT_ID $DEV_ACCOUNT_NO $PRD_ACCOUNT_NO $ASSUME_ROLE_NAME
