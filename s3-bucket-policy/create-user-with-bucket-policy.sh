#!/bin/bash

while getopts u:p: option
do
case "${option}"
in
u) USER=${OPTARG};;
p) POLICY_NAME=${OPTARG};;
esac
done

if [ -z "$USER" ] || [ -z "$POLICY_NAME" ]; then
	echo "Usage ./create-user-with-bucket-policy.sh -u USER -p POLICY_NAME"
	exit 0;
fi

aws iam create-user --user-name $USER

# GET ARN of POLICY
POLICY_ARN=`aws iam list-policies --output text --scope Local | grep test-user-policy3 | awk '{ print $2 }'`

aws iam attach-user-policy --policy-arn $POLICY_ARN --user-name $USER
