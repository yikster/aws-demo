#!python

import boto3
import json
import sys

## TODO refactory for easyread
## TODO remove duplicated paramters
DEV_PROFILE = str(sys.argv[10])
dev_session = boto3.Session(profile_name=DEV_PROFILE)
PRD_PROFILE = str(sys.argv[11])
prd_session = boto3.Session(profile_name=PRD_PROFILE)

pl = dev_session.client('codepipeline')
codebuild = dev_session.client('codebuild')
iam = dev_session.client('iam')
kms = dev_session.client('kms')
cf = dev_session.client('cloudformation')

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

APPROVAL_SNS_ARN = str(sys.argv[9])
print("Step 1: check parameters ARGVS:", str(sys.argv))

approval_policy_arn = "arn:aws:iam::" + DEV_ACCOUNT_NO + ":policy/ApprovalAndDeployToPrd-" + PROJECT_ID
role_arn_deploy_to_product = "arn:aws:iam::{}:role/{}".format(PRD_ACCOUNT_NO, ASSUME_ROLE_NAME)
codepipeline_role_name = "CodeStarWorker-{}-CodePipeline".format(PROJECT_ID)

pipeline_role = None


try:
    pipeline_role = iam.get_role(RoleName=codepipeline_role_name)
except:
    codepipeline_role_name = "CodeStarWorker-{}-ToolChain".format(PROJECT_ID)
    pipeline_role = iam.get_role(RoleName=codepipeline_role_name)


codepipeline_role_arn = pipeline_role["Role"]["Arn"]

print("Step 2: get pipeline role/toolchain role:", pipeline_role)
print("Step 2.1: ASSUME_ROLE OF PIPELINE:", pipeline_role["Role"]["AssumeRolePolicyDocument"])
print("Step 2.2: DEV_CODEPIPELINE_ROLE_ARN:", pipeline_role["Role"]["Arn"])


#res = kms.create_key()
#print(res)
def get_dev_instance_role_arn(project_id, dev_account_no):
    codedeploy = dev_session.client("codedeploy")
    res = codedeploy.batch_get_deployment_groups(
        applicationName=project_id,
        deploymentGroupNames=[
            project_id + "-Env"
        ]
    )

    dev_deployment_role_arn = res["deploymentGroupsInfo"][0]["serviceRoleArn"]
    res = cf.describe_stack_resource(
        StackName="awscodestar-" + project_id,
        LogicalResourceId='WebAppRole'
    )
    dev_instance_role_arn = "arn:aws:iam::{}:role/{}".format(dev_account_no, res["StackResourceDetail"]["PhysicalResourceId"])
    print("---DEV_DEPLOYMENT_GROUP_ARN:", dev_deployment_role_arn)
    #print("PRD_DEPLOYMENT_GROUP_AUTOSCALING_GROUP:", )
    #res = asg.describe_auto_scaling_groups(
    #    AutoScalingGroupNames=[res["deploymentGroupsInfo"][0]["autoScalingGroups"][0]["name"]]
    #)
    #print("ASG_DETAIL:", res)
    #launch_config_name = res["AutoScalingGroups"][0]["LaunchConfigurationName"]

    #res = asg.describe_launch_configurations(
    #    LaunchConfigurationNames=[launch_config_name]
    #)

    return dev_deployment_role_arn, dev_instance_role_arn

dev_deployment_role_arn, dev_instance_role_arn = get_dev_instance_role_arn(PROJECT_ID, DEV_ACCOUNT_NO)

print ("Step 3: get dev account role arns: \n\t\t - deployment: {}\n\t\t - instance:{}".format(dev_deployment_role_arn, dev_instance_role_arn))
def set_prd_env():

    import datetime
    iam = prd_session.client('iam')
    codedeploy = prd_session.client("codedeploy")
    asg = prd_session.client("autoscaling")

    PRD_STS_DEPLOY_ROLE_NAME = ASSUME_ROLE_NAME

    ASSUME_ROLE_POLICY = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": ["codedeploy.amazonaws.com", "kms.amazonaws.com", "s3.amazonaws.com" ]
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
                    "AWS": ["arn:aws:iam::{}:role/CodeStarWorker-{}-ToolChain".format(DEV_ACCOUNT_NO, PROJECT_ID) ]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        res = iam.get_role(RoleName=PRD_STS_DEPLOY_ROLE_NAME)
        print("PRD_STS_DEPLOY_ROLE is exist")
    except:
        res = iam.create_role(RoleName=PRD_STS_DEPLOY_ROLE_NAME,
                              AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY))
        print("PRD_STS_DEPLOY_ROLE is created", res)

    res = codedeploy.batch_get_deployment_groups(
        applicationName=PRODUCT_APP,
        deploymentGroupNames=[
            PRODUCT_DEPLOYMENT_GROUP,
        ]
    )
    iam.attach_role_policy(RoleName=PRD_STS_DEPLOY_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess")
    iam.attach_role_policy(RoleName=PRD_STS_DEPLOY_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AWSCodeDeployFullAccess")
    iam.attach_role_policy(RoleName=PRD_STS_DEPLOY_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole")

    iam.put_role_policy(
        RoleName=PRD_STS_DEPLOY_ROLE_NAME,
        PolicyName="KMS_FULL_INLINE",
        PolicyDocument= json.dumps({
            "Version": "2012-10-17",
            "Statement": [{ "Sid": "kmsfull", "Effect":"Allow", "Action":"kms:*", "Resource":"*"}]})
    )
    '''
    iam.put_role_policy(
        RoleName=PRD_STS_DEPLOY_ROLE_NAME,
        PolicyName="RevokeOldSession-" + PROJECT_ID,
        PolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Deny",
                        "Action": [
                            "*"
                        ],
                        "Resource": [
                            "*"
                        ],
                        "Condition": {
                            "DateLessThan": {
                                "aws:TokenIssueTime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                            }
                        }
                    }
                ]
            })
    )
    '''

    prd_deployment_role_arn = res["deploymentGroupsInfo"][0]["serviceRoleArn"]
    print("PRD_DEPLOYMENT_GROUP_ARN:", prd_deployment_role_arn)
    print("PRD_DEPLOYMENT_GROUP_AUTOSCALING_GROUP:", )
    res = asg.describe_auto_scaling_groups(
        AutoScalingGroupNames=[res["deploymentGroupsInfo"][0]["autoScalingGroups"][0]["name"]]
    )
    print("ASG_DETAIL:", res)
    launch_config_name = res["AutoScalingGroups"][0]["LaunchConfigurationName"]

    res = asg.describe_launch_configurations(
        LaunchConfigurationNames=[ launch_config_name ]
    )

    print("ASG_CFG_DETAIL:", res)

    prd_instance_profile = res["LaunchConfigurations"][0]["IamInstanceProfile"]
    res = iam.get_instance_profile(
        InstanceProfileName=prd_instance_profile
    )

    print("InstanceProfileDetail:", res)
    prd_instance_role_arn = res["InstanceProfile"]["Roles"][0]["Arn"]

    return prd_deployment_role_arn, prd_instance_role_arn

print("Step 5: Set production roles")
prd_deployment_role_arn, prd_instance_role_arn = set_prd_env()

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

def add_permission_on_s3(region, devAccountNo, PROJECT_ID, prodAccountNo, prd_deployment_role_arn, prd_instance_role_arn, dev_instance_role_arn):
    s3 = dev_session.client("s3")

    bucket_name = "aws-codestar-{}-{}-{}-pipe".format(region, devAccountNo, PROJECT_ID)
    AWS_PRINCIPAL_ARN = "arn:aws:iam::{}:root".format(prodAccountNo)
    BUCKET_ARN = "arn:aws:s3:::{}".format(bucket_name)
    BUCKET_OBJECT_ARN = "arn:aws:s3:::{}/*".format(bucket_name)
    policy_for_product = {
        "Sid": "PrdDeploy_Automation",
        "Effect": "Allow",
        "Principal": {
            "AWS": [
                codepipeline_role_arn,
                dev_instance_role_arn,
                AWS_PRINCIPAL_ARN,
                prd_deployment_role_arn,
                prd_instance_role_arn
            ]
        },
        "Action": [
            "s3:*"
        ],
        "Resource": [ BUCKET_ARN, BUCKET_OBJECT_ARN ]
    }

    print("BUCKET_NAME:", bucket_name)
    res = s3.get_bucket_policy(Bucket=bucket_name )
    curr_policy = json.loads(res["Policy"])

    print("POLICY_KEYS:", curr_policy.keys() )

    print(curr_policy["Statement"])
    policy_exist = False
    for i in range(len(curr_policy["Statement"])):
        if "PrdDeploy_Automation" == curr_policy["Statement"][i]["Sid"]:
            curr_policy["Statement"][i] = policy_for_product
            policy_exist = True
            break


    new_policy = { "Version" : "2012-10-17", "Statement":[]}
    new_policy["Statement"] = curr_policy["Statement"]


    print("POLICY_EXIST:", policy_exist)
    if False == policy_exist:
        new_policy["Statement"].append(policy_for_product)

    print("BUCKET_POLOCY:", json.dumps(new_policy))
    s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(new_policy))


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

# TODO add assume role to pipeline, trust relationship
## get_assume_role



def add_assume_role_to_pipeline(pipeline_role, prd_account_no):
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
                    "AWS": [ "arn:aws:iam::" + prd_account_no + ":root",role_arn_deploy_to_product ]
                },
                "Action": "sts:AssumeRole"
            }
        )
        print("\t\t", json.dumps(assume_role_policy))
        iam.update_assume_role_policy(RoleName=codepipeline_role_name, PolicyDocument=json.dumps(assume_role_policy))


print("Step 4: add assume_role to pipeline")
add_assume_role_to_pipeline(pipeline_role, PRD_ACCOUNT_NO)

pipeline_role = None

def attach_approval_policy(approval_policy_arn, prd_account_no, assume_role_name):
    # TODO get publish policy
    try:
        exist_policy = iam.get_policy(PolicyArn=approval_policy_arn)
        print("EXIST_POLICY:", exist_policy)

    except:
        PolicyDocument = {
            "Version": "2012-10-17",
            "Statement": [
                IAM_SNS_PUBLISH,
                {
                    "Sid":"DeployAssumeRole",
                    "Effect":"Allow",
                    "Resource": [ "arn:aws:iam::" + PRD_ACCOUNT_NO + ":role/" + ASSUME_ROLE_NAME , prd_deployment_role_arn ],
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        print("Policy-ApprovalAdnDeployToPrd:", PolicyDocument)
        iam.create_policy(PolicyName="ApprovalAndDeployToPrd-" + PROJECT_ID, PolicyDocument=json.dumps(PolicyDocument))
        print("CREATE_POLICY")

    print("CODEPIPELINE_ROLE:", codepipeline_role_name)
    print("CODEPIPELINE_ROLE_POLICY:", approval_policy_arn)

    res = iam.attach_role_policy(RoleName=codepipeline_role_name, PolicyArn=approval_policy_arn)
    print("ATTACH_POLICY:", res)




print("Step 6: add approval policy to prd")
attach_approval_policy(approval_policy_arn, PRD_ACCOUNT_NO, ASSUME_ROLE_NAME)

print("Step 7: Add Approval and DeployPrd to Codestar project pipeline")

print("Step 7.1: get current pipeline")
new_pipeline = get_pipeline(PROJECT_ID, role_arn_deploy_to_product, PRODUCT_APP, PRODUCT_DEPLOYMENT_GROUP)
artifactStore = new_pipeline["artifactStore"]
artifactStore["encryptionKey"] = { "id" : KMS_ARN, "type":"KMS" }

## Key 를 넣으면 에러가..
#artifactStore.pop("encryptionKey", None)

dev_instance_role = ""

print("PRD_INS_ROLE_ARN:", prd_instance_role_arn)
print("DEV_INS_ROLE_ARN:", dev_instance_role_arn)

print("Step 8: add DEV kms policy for prd role's access")
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
                        if dev_instance_role_arn in state["Principal"]["AWS"] and prd_instance_role_arn in state["Principal"]["AWS"] :
                            policy_added = True

                        else:
                            state["Principal"]["AWS"].extend([dev_instance_role_arn, prd_instance_role_arn])
                            state["Principal"]["AWS"] = list(set(state["Principal"]["AWS"]))
                            statements[i] = state
                            pliicy_added = True

                policy["Statement"] = statements

                if False == policy_added:
                    policy["Statement"].append({
                        "Sid": KMS_POLICY_SID,
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [dev_instance_role_arn, prd_instance_role_arn, dev_deployment_role_arn, prd_deployment_role_arn]
                        },
                        "Action": [
                            "kms:Encrypt",
                            "kms:Decrypt",
                            "kms:ReEncrypt*",
                            "kms:GenerateDataKey*",
                            "kms:DescribeKey"
                        ],
                        "Resource": "*"
                    })



                print("KMS_POLOCY_DOCUMENT:", json.dumps(policy))
                kms.put_key_policy(
                    KeyId=KMS_ARN,
                    PolicyName='default',
                    Policy=json.dumps(policy)
                )





print("Step 9: add kms encryption key into build stage")

## codebuild
current_codebuild = codebuild.batch_get_projects(names=[PROJECT_ID])
current_codebuild["projects"][0]["encryptionKey"] = KMS_ARN

res = codebuild.update_project(name=PROJECT_ID, encryptionKey=KMS_ARN)
print("CODEBUILD_UPDATE_PROJECT_RESULT:", res)

## Add KMS
new_pipeline["artifactStore"] = artifactStore

print(new_pipeline)

print("Step 10: add permissions for access dev artifact to prd_roles and dev_roles")
add_permission_on_s3(REGION, DEV_ACCOUNT_NO, PROJECT_ID, PRD_ACCOUNT_NO, prd_deployment_role_arn, prd_instance_role_arn, dev_instance_role_arn)

## TODO revoke role
# Should  revoke dev-pipeline/toolchain role

## GET NEW SESSION (role is updated)

import time

t=60
while t > 0:
    print( str(t) + " seconds left..")
    time.sleep(1)
    t-=1

print("Step 11: update pipeline")

updated_dev_session = boto3.Session(profile_name=DEV_PROFILE)
codepipeline = updated_dev_session.client("codepipeline")
codepipeline.update_pipeline(pipeline=new_pipeline)
## ERRROR
## botocore.errorfactory.InvalidStructureException: An error occurred (InvalidStructureException) when calling the UpdatePipeline operation: arn:aws:iam::125492839279:role/CodeStarWorker-java-ec2-02-ToolChain is not authorized to perform AssumeRole on role arn:aws:iam::174548683514:role/STSDeployToPrdFromDevAccount
#Fix 1 attach codedeploy_permission & assumerole
#Fix 2 attach ToolChain assumerole is added PRD_STS_ROLE
## Maybe it takes time ( it works , two hours later , there was error at that time)

## TODO python add permission to s3
#Fix 3 : Unable to access the artifact with Amazon S3 object key 'key' located in the Amazon S3 artifact bucket 'bucket'. The provided role does not have sufficient permissions.
## doenst workadd "arn:aws:iam::125492839279:role/CodeStarWorker-php-ec2-01-ToolChain", to production_deployment_role

## TODO python add permission to STS--PHP S3 Full, KMS Full
#Fix 4 : Add permissions to STSDeployToPrdFromDevAccountPHP, S3 Full, KMS Full
#Fix 5 revoke ToolChain (dev) STS(prd) session

#Fix Final : remove bode permission on dev_account's ToolChain permission


print("# of stages", len(new_pipeline['stages']))

#print(json.dumps(result, default=json_util.default))
