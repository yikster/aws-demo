#!python

import boto3
import json

pl = boto3.client('codepipeline')
iam = boto3.client('iam')

IAM_SNS_PUBLISH = {
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "*"
}
PRD_ACCOUNT_NO = "1234567890"
ASSUME_ROLE_NAME = "STSDeployToPrdFromDevAccount"
DEV_ACCOUNT_NO = "1234567899"
REGION="ap-northeast-2"
PROJECT_ID = "dev-java-ec2"

policy_arn = "arn:aws:iam::{}:policy/ApprovalAndDeployToPrd".format(DEV_ACCOUNT_NO)
role_arn_deploy_to_product = "arn:aws:iam::1234567890:role/STSDeployToPrdFromDevAccount"

projectId = "dev-java-ec2"

def get_assume_role(accountNo, rolename):
    arn = "arn:aws:iam::{}:role/{}".format(accountNo, rolename)
    ASSUME_ROLE_CODEDEPLOY = {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Resource": [
        arn
        ]
    }
codepipeline_role_name = "CodeStarWorker-{}-CodePipeline".format(projectId)

new_role = iam.get_role(RoleName=codepipeline_role_name)

new_role["Role"]["AssumeRolePolicyDocument"]["Statement"].append(IAM_SNS_PUBLISH)
new_role["Role"]["AssumeRolePolicyDocument"]["Statement"].append(get_assume_role(PRD_ACCOUNT_NO, ASSUME_ROLE_NAME))

PolicyDocument = new_role["Role"]["AssumeRolePolicyDocument"]
PolicyDocument["Version"]="2012-10-17"
print(PolicyDocument)

try:
    iam.create_policy(PolicyName="ApprovalAndDeployToPrd", PolicyDocument=json.dumps(PolicyDocument))
except:
    print("Fail to create policy")

def add_permission_on_s3(region, devAccountNo, projectId, prodAccountNo):
    s3 = boto3.client("s3")

    bucket_name = "aws-codestar-{}-{}-{}-pipe".format(region, devAccountNo, projectId)
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


def get_pipeline(projectId, role_arn_deploy_to_product):
    pipeline_name = "{}-Pipeline".format(projectId)
    application_name = "{}-app".format(projectId)
    deployment_group_name = "{}-dg".format(projectId)
    build_artifact_name = "{}-BuildArtifact".format(projectId)
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


# TODO get publish policy
try:
    iam.get_policy(PolicyArn=policy_arn)
except:
    iam.create_policy(PolicyName="ApprovalAndDeployToPrd")

iam.attach_role_policy(RoleName=codepipeline_role_name, PolicyArn=policy_arn)


new_pipeline = get_pipeline(projectId, role_arn_deploy_to_product)

print(new_pipeline)

#add_permission_on_s3(REGION, DEV_ACCOUNT_NO, PROJECT_ID, PROD_ACCOUNT_NO)

pl.update_pipeline(pipeline=new_pipeline)

print("# of stages", len(new_pipeline['stages']))

#print(json.dumps(result, default=json_util.default))
