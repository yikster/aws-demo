#!python

import boto3
import json
import sys

pl = boto3.client('codepipeline')
codebuild = boto3.client('codebuild')
iam = boto3.client('iam')
kms = boto3.client('kms')
cf = boto3.client('cloudformation')

# python codepipeline.py $REGION $PROJECT_ID $DEV_ACCOUNT_NO $PRD_ACCOUNT_NO $ASSUME_ROLE_NAME

IAM_SNS_PUBLISH = { "Effect": "Allow", "Action": "sns:Publish", "Resource": "*" }
KMS_POLICY_SID = "Added by pipelineautomation"

## PRD Account must have s3 get api call permission
## KMS - https://aws.amazon.com/ko/blogs/security/share-custom-encryption-keys-more-securely-between-accounts-by-using-aws-key-management-service/

## SET INPUT PARAMETERS
REGION = str(sys.argv[1])
PROJECT_ID = str(sys.argv[2])
DEV_ACCOUNT_NO = str(sys.argv[3])
PRD_ACCOUNT_NO = str(sys.argv[4])
ASSUME_ROLE_NAME = str(sys.argv[5])
PRODUCT_APP = str(sys.argv[6])
PRODUCT_DEPLOYMENT_GROUP = str(sys.argv[7])
KMS_ARN = str(sys.argv[8])
DEV_INSTANCE_ROLE_ARN = str(sys.argv[9])
PRD_INSTANCE_ROLE_ARN = str(sys.argv[10])
print("PRD_INS_ROLE_ARN:", PRD_INSTANCE_ROLE_ARN)

APPROVAL_SNS_ARN = str(sys.argv[11])
PRD_CODEDEPLOY_ARN = "abcde"
#PRD_CODEDEPLOY_ARN = str(sys.argv[12])
print("ARGVS:", str(sys.argv))

policy_arn = "arn:aws:iam::{}:policy/ApprovalAndDeployToPrd".format(DEV_ACCOUNT_NO)
role_arn_deploy_to_product = "arn:aws:iam::{}:role/{}".format(PRD_ACCOUNT_NO, ASSUME_ROLE_NAME)
codepipeline_role_name = "CodeStarWorker-{}-CodePipeline".format(PROJECT_ID)


try:
    pipeline_role = iam.get_role(RoleName=codepipeline_role_name)
except:
    codepipeline_role_name = "CodeStarWorker-{}-ToolChain".format(PROJECT_ID)
    pipeline_role = iam.get_role(RoleName=codepipeline_role_name)


codepipeline_role_arn = pipeline_role["Role"]["Arn"]

print("CODEPIPELINE_ROLE:", pipeline_role)
print("ASSUME_ROLE OF PIPELINE:", pipeline_role["Role"]["AssumeRolePolicyDocument"])
print("DEV_CODEPIPELINE_ROLE_ARN:", pipeline_role["Role"]["Arn"])


#res = kms.create_key()
#print(res)

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



## TODO artifact s3에 prd_codedeploy_role 권한 추가 필
def add_permission_on_s3(region, devAccountNo, PROJECT_ID, prodAccountNo):
    s3 = boto3.client("s3")

    bucket_name = "aws-codestar-{}-{}-{}-pipe".format(region, devAccountNo, PROJECT_ID)
    AWS_PRINCIPAL_ARN = "arn:aws:iam::{}:root".format(prodAccountNo)
    BUCKET_ARN = "arn:aws:s3:::{}".format(bucket_name)
    BUCKET_OBJECT_ARN = "arn:aws:s3:::{}/*".format(bucket_name)
    policy_for_product = [
        {
            "Sid": "PrdDeploy_Automation",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    codepipeline_role_arn,
                    DEV_INSTANCE_ROLE_ARN,
                    AWS_PRINCIPAL_ARN,
                    PRD_CODEDEPLOY_ARN,
                    PRD_INSTANCE_ROLE_ARN
                ]
            },
            "Action": [
                "s3:*"
            ],
            "Resource": [ BUCKET_OBJECT_ARN, BUCKET_OBJECT_ARN ]
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


def get_pipeline(PROJECT_ID, role_arn_deploy_to_product, application_name, deployment_group_name):
    pipeline_name = "{}-Pipeline".format(PROJECT_ID)
    build_artifact_name = "{}-BuildArtifact".format(PROJECT_ID)
    result = pl.get_pipeline(name=pipeline_name)
    print("CURRENT_PIPELINE:", pipeline_name)
    print("CURRENT_PIPELINE_DETAIL:", result)
    pipeline = result['pipeline']

    stages = pipeline['stages']
    ## check Approval and DeployProd exists

    approval_stage_exist = False
    deploy_product_stage_exist = False

    for stage in stages:
        if "ManualApproval" == stage["name"]:
            approval_stage_exist = True
        elif "DeployProduction" == stage["name"]:
            deploy_product_stage_exist = True

    approval_stage = {
        "name": "ManualApproval",
        "actions": [
            {
                "name": "ManualApproval",
                "actionTypeId": {
                    "category": "Approval",
                    "owner": "AWS",
                    "provider": "Manual",
                    "version": "1"
                },
                "runOrder": 1,
                "configuration": {
                    "CustomData": "Last dev version is required an approval",
                    "ExternalEntityLink": "http://example.com",
                    "NotificationArn": APPROVAL_SNS_ARN
                },
                "outputArtifacts": [],
                "inputArtifacts": []
            }
        ]
    }

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
    if False == approval_stage_exist:
        stages.append(approval_stage)
    ## without adding prd deploy
    if False == deploy_product_stage_exist:
        stages.append(newDeployStage)

    pipeline['stages'] = stages
    return pipeline

# TODO pipeline에 AssumeRole을 넣을 것 trust relationship
## get_assume_role
pipeline_role = None



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
        print("CREATE_POLICY")

    print("CODEPIPELINE_ROLE:", codepipeline_role_name)
    print("CODEPIPELINE_ROLE_POLICY:", policy_arn)

    res = iam.attach_role_policy(RoleName=codepipeline_role_name, PolicyArn=policy_arn)
    print("ATTACH_POLICY:", res)


attach_approval_policy(policy_arn, PRD_ACCOUNT_NO, ASSUME_ROLE_NAME)

new_pipeline = get_pipeline(PROJECT_ID, role_arn_deploy_to_product, PRODUCT_APP, PRODUCT_DEPLOYMENT_GROUP)
artifactStore = new_pipeline["artifactStore"]
artifactStore["encryptionKey"] = { "id" : KMS_ARN, "type":"KMS" }

## Key 를 넣으면 에러가..
#artifactStore.pop("encryptionKey", None)

dev_instance_role = ""

print("PRD_INS_ROLE_ARN:", PRD_INSTANCE_ROLE_ARN)
print("DEV_INS_ROLE_ARN:", DEV_INSTANCE_ROLE_ARN)
## IAM_instance_profile_DEV
for stage in new_pipeline["stages"]:
    if "Deploy" == stage["name"] and 3 == len(stage["actions"]):
        for action in stage["actions"]:
            if action["configuration"] != "" and "ParameterOverrides" in action["configuration"]:
                INSTANCE_PROFILE_NAME = json.loads(action["configuration"]["ParameterOverrides"])["WebAppInstanceProfile"]
                res = iam.get_instance_profile(InstanceProfileName=INSTANCE_PROFILE_NAME)

                dev_instance_role = res["InstanceProfile"]["Roles"][0]["Arn"]

                print("DEV_INSTANCE_ROLE:", dev_instance_role)
                res = kms.get_key_policy(KeyId=KMS_ARN, PolicyName="default")
                policy = json.loads(res["Policy"])
                statements = policy["Statement"]
                policy_added = False
                for i in range(len(statements)):
                    state = statements[i]
                    if state["Sid"] == KMS_POLICY_SID and "Principal" in state and "AWS" in state["Principal"] and type(state["Principal"]["AWS"]) is list:
                        if DEV_INSTANCE_ROLE_ARN in state["Principal"]["AWS"] and PRD_INSTANCE_ROLE_ARN in state["Principal"]["AWS"] :
                            policy_added = True

                        else:
                            state["Principal"]["AWS"].extend([DEV_INSTANCE_ROLE_ARN, PRD_INSTANCE_ROLE_ARN])
                            state["Principal"]["AWS"] = list(set(state["Principal"]["AWS"]))
                            statements[i] = state
                policy["Statement"] = statements

                print("KMS_POLOCY_DOCUMENT:", policy)
                ###
                #kms.put_key_policy(
                #    KeyId=KMS_ARN,
                #    PolicyName='default',
                ##    Policy=json.dumps(policy)
                #)
                ###




## codebuild
current_codebuild = codebuild.batch_get_projects(names=[PROJECT_ID])
current_codebuild["projects"][0]["encryptionKey"] = KMS_ARN

res = codebuild.update_project(name=PROJECT_ID, encryptionKey=KMS_ARN)
print("CODEBUILD_UPDATE_PROJECT_RESULT:", res)

## Add KMS
new_pipeline["artifactStore"] = artifactStore

print(new_pipeline)

#add_permission_on_s3(REGION, DEV_ACCOUNT_NO, PROJECT_ID, PROD_ACCOUNT_NO)

pl.update_pipeline(pipeline=new_pipeline)
## ERRROR
## botocore.errorfactory.InvalidStructureException: An error occurred (InvalidStructureException) when calling the UpdatePipeline operation: arn:aws:iam::125492839279:role/CodeStarWorker-java-ec2-02-ToolChain is not authorized to perform AssumeRole on role arn:aws:iam::174548683514:role/STSDeployToPrdFromDevAccount
print("# of stages", len(new_pipeline['stages']))

#print(json.dumps(result, default=json_util.default))
