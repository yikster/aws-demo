
#!python
import boto3
import json
import sys

iam = boto3.client('iam')


PROJECT_ID=str(sys.argv[1])
DEV_ACCOUNT_NO=str(sys.argv[2])
PRD_STS_DEPLOY_ROLE_NAME="PRD_DEPLOY_STS_{}".format(PROJECT_ID)


ASSUME_ROLE_POLICY={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS":
                        "arn:aws:iam::{}:role/CodeStarWorker-{}-ToolChain".format(DEV_ACCOUNT_NO, PROJECT_ID)
                    ,
                    "Service": "codedeploy.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::{}:root".format(DEV_ACCOUNT_NO)
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::{}:role/CodeStarWorker-{}-ToolChain".format(DEV_ACCOUNT_NO, PROJECT_ID)
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
try:
    res = iam.get_role(RoleName=PRD_STS_DEPLOY_ROLE_NAME)
    print("PRD_STS_DEPLOY_ROLE is exist")
except:
    res = iam.create_role (RoleName=PRD_STS_DEPLOY_ROLE_NAME, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY))
    print("PRD_STS_DEPLOY_ROLE is created", res)
