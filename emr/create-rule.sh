#!/bin/bash

TARGET_ARN=arn:aws:lambda:ap-northeast-2:519590242672:function:snsToSlack
CLUSTER_ID=$1
EVENT_PATTERN='{
  "source": [
    "aws.emr"
  ],
  "detail-type": [
    "EMR Auto Scaling Policy State Change",
    "EMR Step Status Change",
    "EMR Cluster State Change",
    "EMR Instance Group State Change",
    "EMR Instance Fleet State Change"
  ],
  "detail": {
    "clusterId": [
      "'"${CLUSTER_ID}"'"
    ]
  }
}'

echo $CLUSTER_ID
echo $TARGET_ARN
echo $EVENT_PATTERN

RULE_NAME=CWE-EMR-"${CLUSTER_ID}" 

RULE_ID=`aws events put-rule --output text --name "${RULE_NAME}" --event-pattern "${EVENT_PATTERN}"`
aws lambda add-permission --function-name snsToSlack --action "lambda:InvokeFunction" --principal events.amazonaws.com --source-arn arn:aws:events:ap-northeast-2:519590242672:rule/"${RULE_NAME}" --statement-id stmt-id-"${RULE_NAME}"
aws events put-targets --rule "${RULE_NAME}" --targets "Id"="1","Arn"=""${TARGET_ARN}""
aws events enable-rule --name "${RULE_NAME}"
aws events describe-rule --name "${RULE_NAME}"
