#!/bin/bash

while getopts b:p: option
do
case "${option}"
in
b) BUCKET_NAME=${OPTARG};;
p) POLICY_NAME=${OPTARG};;
esac
done

if [ -z "$BUCKET_NAME" ] || [ -z "$POLICY_NAME" ]; then
	echo "Usage ./create-policy.sh -b BUCKET_NAME -p POLICY_NAME"
	exit 0;
fi
POLICY_DOCUMENT="{ \
    \"Version\": \"2012-10-17\",	\
    \"Statement\": [	\
        {	\
            \"Sid\": \"VisualEditor0\",	\
            \"Effect\": \"Allow\",		\
            \"Action\": [				\
                \"s3:PutObject\",		\
                \"s3:GetObject\",		\
                \"s3:ListBucket\",		\
                \"s3:DeleteObject\"		\
            ],							\
            \"Resource\": [				\
                \"arn:aws:s3:::${BUCKET_NAME}\",	\
                \"arn:aws:s3:::${BUCKET_NAME}/*\"	\
            ]	\
        }	\
    ]	\
}	"
echo "Policy is below..."
echo $POLICY_DOCUMENT

echo "creating policy..."
aws iam create-policy --policy-name $POLICY_NAME --policy-document "${POLICY_DOCUMENT}"
