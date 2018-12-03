#!python

import boto3
import json
import sys

pl = boto3.client('codepipeline')
iam = boto3.client('iam')

# python codepipeline.py $REGION $PROJECT_ID $DEV_ACCOUNT_NO $PRD_ACCOUNT_NO $ASSUME_ROLE_NAME

IAM_SNS_PUBLISH = { "Effect": "Allow", "Action": "sns:Publish", "Resource": "*" }

## SET INPUT PARAMETERS
REGION = str(sys.argv[1])
PROJECT_ID = str(sys.argv[2])
DEV_ACCOUNT_NO = str(sys.argv[3])
PRD_ACCOUNT_NO = str(sys.argv[4])
ASSUME_ROLE_NAME = str(sys.argv[5])


print("ARGVS:", str(sys.argv))

policy_arn = "arn:aws:iam::{}:policy/ApprovalAndDeployToPrd".format(DEV_ACCOUNT_NO)
role_arn_deploy_to_product = "arn:aws:iam::{}:role/{}".format(PRD_ACCOUNT_NO, ASSUME_ROLE_NAME)
codepipeline_role_name = "CodeStarWorker-{}-CodePipeline".format(PROJECT_ID)

def gen_assume_role_for_root(accountNo):
    print("AssumeRole Aready added")


def get_assume_role(accountNo, rolename):
    assume_role_to_arn = {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Resource": [
            "arn:aws:iam::{}:role/{}".format(accountNo, rolename)
        ]
    }
    return assume_role_to_arn


def add_permission_on_s3(region, devAccountNo, PROJECT_ID, prodAccountNo):
    s3 = boto3.client("s3")

    bucket_name = "aws-codestar-{}-{}-{}-pipe".format(region, devAccountNo, PROJECT_ID)
    AWS_PRINCIPAL_ARN = "arn:aws:iam::{}:root".format(prodAccountNo)
    BUCKET_ARN = "arn:aws:s3:::{}".format(bucket_name)
    BUCKET_OBJECT_ARN = "arn:aws:s3:::{}/*".format(bucket_name)
    policy_for_product = [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "AWS": AWS_PRINCIPAL_ARN
            },
            "Action": [
                "s3:Get*",
                "s3:Put*"
            ],
            "Resource": BUCKET_OBJECT_ARN
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "AWS": AWS_PRINCIPAL_ARN
            },
            "Action": "s3:ListBucket",
            "Resource": BUCKET_ARN
        }]

    print("BUCKET_NAME:", bucket_name)
    res = s3.get_bucket_policy(Bucket=bucket_name )
    curr_policy = json.loads(res["Policy"])

    print("POLICY_KEYS:", curr_policy.keys() )

    print(curr_policy["Statement"])
    new_policy = { "Version" : "2012-10-17", "Statement":[]}
    new_policy["Statement"] = curr_policy["Statement"]
    new_policy["Statement"].extend(policy_for_product)

    s3.put_bucket_policy(Bucket=bucket_name, Policy=new_policy)


def get_pipeline(PROJECT_ID, role_arn_deploy_to_product):
    pipeline_name = "{}-Pipeline".format(PROJECT_ID)
    application_name = "{}-app".format(PROJECT_ID)
    deployment_group_name = "{}-dg".format(PROJECT_ID)
    build_artifact_name = "{}-BuildArtifact".format(PROJECT_ID)
    result = pl.get_pipeline(name=pipeline_name)

    pipeline = result['pipeline']

    stages = pipeline['stages']
    newDeployStage = {'name': 'DeployProduction',
        'actions': [{'name': 'DeployProduction',
        'actionTypeId': {'category': 'Deploy',
        'owner': 'AWS',
        'provider': 'CodeDeploy',
        'version': '1'},
        'runOrder': 1,
        "roleArn": role_arn_deploy_to_product,
        'configuration':
        {
            "ApplicationName": application_name,
            "DeploymentGroupName": deployment_group_name
        },
        'outputArtifacts': [],
        'inputArtifacts': [
            {'name': build_artifact_name}
        ]}
    ]}
    stages.append(newDeployStage)
    return pipeline

# TODO pipeline에 AssumeRole을 넣을 것 trust relationship
## get_assume_role
pipeline_role = iam.get_role(RoleName=codepipeline_role_name)
print("CODEPIPELINE_ROLE:", pipeline_role)
print("ASSUME_ROLE OF PIPELINE:", pipeline_role["Role"]["AssumeRolePolicyDocument"])


def add_assume_role_into_pipeline(pipeline_role, prd_account_no):
    contains_prd_account_assumerole = False
    for statement in pipeline_role["Role"]["AssumeRolePolicyDocument"]["Statement"]:
        if (statement["Action"] == "sts:AssumeRole" and "AWS" in statement["Principal"]) and prd_account_no in statement["Principal"]["AWS"]:
            # TODO add assumerole into pipeline assumerole_policy
            contains_prd_account_assumerole = True
            print("AssumeRole Aready added")

            break

    if False == contains_prd_account_assumerole:
        assume_role_policy = pipeline_role["Role"]["AssumeRolePolicyDocument"]
        assume_role_policy["Statement"].append(
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::" + prd_account_no + ":root"
                },
                "Action": "sts:AssumeRole"
            }
        )
        iam.update_assume_role_policy(RoleName=codepipeline_role_name, PolicyDocument=json.dumps(assume_role_policy))


def attach_approval_policy(policy_arn, prd_account_no, assume_role_name):
    # TODO get publish policy
    try:
        exist_policy = iam.get_policy(PolicyArn=policy_arn)
        print("EXIST_POLICY:", exist_policy)

    except:
        PolicyDocument = {"Version": "2012-10-17",
                          "Statement": [IAM_SNS_PUBLISH, get_assume_role(prd_account_no, assume_role_name)]}
        iam.create_policy(PolicyName="ApprovalAndDeployToPrd", PolicyDocument=json.dumps(PolicyDocument))

    iam.attach_role_policy(RoleName=codepipeline_role_name, PolicyArn=policy_arn)


attach_approval_policy(policy_arn, PRD_ACCOUNT_NO, ASSUME_ROLE_NAME)
new_pipeline = get_pipeline(PROJECT_ID, role_arn_deploy_to_product)

print(new_pipeline)

#add_permission_on_s3(REGION, DEV_ACCOUNT_NO, PROJECT_ID, PROD_ACCOUNT_NO)

pl.update_pipeline(pipeline=new_pipeline)

print("# of stages", len(new_pipeline['stages']))

#print(json.dumps(result, default=json_util.default))
