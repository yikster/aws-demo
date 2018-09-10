#!/bin/bash
if [[ $# -lt 13 ]] ; then
  echo "Arguments should be 12"
  echo "Usages: ./create-emr.sh cluster_name core_instance_type core_instance_nodes master_instance_type subnet_id master_security_group_id slave_security_group_id keypair_name executor_memory driver_memory driver_cores core_volume_size aws_profile"
  exit 1
fi 

KEY_NAME="$8"
SUBNET_ID="$5"
MASTER_SECURITY_GROUP_ID="$6"
SLAVE_SECURITY_GROUP_ID="$7"
CLUSTER_NAME="$1"
INSTANCE_TYPE="$2"
EXECUTOR_MEMORY="$9"
DRIVER_MEMORY="${10}"
DRIVER_CORES="${11}"
CORE_NODES=$3
START_TIME=$(date)
CORE_VOLUME=${12}
CUSTOM_AMI_ID="ami-d7dc71b9"
MASTER_INSTANCE_TYPE=$4
AWS_PROFILE="${13}"
#--custom-ami-id "${CUSTOM_AMI_ID}" 

LAST_BID_PRICE=`aws ec2 describe-spot-price-history --profile "${AWS_PROFILE}" --instance-type="${INSTANCE_TYPE}" --start-time="${START_TIME}" --output text --availability-zone=ap-northeast-2a --product-descriptions="Linux/UNIX" | awk '{print $5+0.001}'`
BID_PRICE=`printf '%.*f' 3 $LAST_BID_PRICE`

echo 'BID_PRICE=${BID_PRICE}'

LAST_MASTER_BID_PRICE=`aws ec2 describe-spot-price-history --profile "${AWS_PROFILE}" --instance-type="${MASTER_INSTANCE_TYPE}" --start-time="${START_TIME}" --output text --availability-zone=ap-northeast-2a --product-descriptions="Linux/UNIX" | awk '{print $5+0.001}'`
MASTER_BID_PRICE=`printf '%.*f' 3 $LAST_MASTER_BID_PRICE`

#--bootstrap-actions '[{"Path":"s3://aws-bigdata-blog/artifacts/Turbocharge_Apache_Hive_on_EMR/configure-Hive-LLAP.sh","Name":"Bootstrap"}]' \ 

CLUSTER_ID=`aws emr create-cluster --profile "${AWS_PROFILE}" --output text --applications Name=Hadoop Name=Hive Name=Spark Name=Tez Name=Livy Name=Flink Name=Ganglia Name=HBase Name=Pig Name=Presto Name=Hue Name=MXNet Name=ZooKeeper Name=Oozie Name=HCatalog \
--enable-debugging \
--log-uri s3://kyoungsu-aws-logs-icn/emr/"${CLUSTER_NAME}"/ \
--service-role EMR_DefaultRole \
--release-label emr-5.11.1 --name "${CLUSTER_NAME}" \
--region ap-northeast-2 \
--configurations file://configurations.json \
--ec2-attributes '{  
  "KeyName":"'"${KEY_NAME}"'",
  "InstanceProfile":"EMR_EC2_DefaultRole",
  "SubnetId":"'"${SUBNET_ID}"'",
  "EmrManagedSlaveSecurityGroup":"'"${MASTER_SECURITY_GROUP_ID}"'",
  "EmrManagedMasterSecurityGroup":"'"${SLAVE_SECURITY_GROUP_ID}"'"
}' \
--instance-groups '[  
  {  
    "InstanceCount":1,
    "InstanceGroupType":"MASTER",
    "InstanceType":"m4.xlarge",
    "Name":"Master instance group - 1",
    "BidPrice": "'"${MASTER_BID_PRICE}"'"
  },
  {  
    "InstanceCount":'${CORE_NODES}',
    "EbsConfiguration":{  
      "EbsBlockDeviceConfigs":[  
        {  
          "VolumeSpecification":{  
            "SizeInGB":'"${CORE_VOLUME}"',
            "VolumeType":"gp2"
          },
          "VolumesPerInstance":2
        }
      ],
      "EbsOptimized":false
    },
    "InstanceGroupType":"CORE",
    "InstanceType":"'"${INSTANCE_TYPE}"'",
    "Name":"Core instance group - 2",
    "BidPrice": "'"${BID_PRICE}"'"
  }
]' \
--steps '[
    {
        "Name":"HiveCreateTable",
        "ActionOnFailure":"CONTINUE",
        "Type":"CUSTOM_JAR",
        "Jar":"command-runner.jar",
        "Args":["hive-script", "--run-hive-script", "--args", "-f", "s3://awsdemo-ap-northeast-2/aws-blog-spark-parquet-conversion/createtable.hql"]
    },
    {
        "Name":"HiveAddPartitions",
        "ActionOnFailure":"CONTINUE",
        "Type":"CUSTOM_JAR",
        "Jar":"command-runner.jar",
        "Args":["hive-script", "--run-hive-script", "--args", "-f", "s3://awsdemo-ap-northeast-2/aws-blog-spark-parquet-conversion/addpartitions.hql","-d","OUTPUT=s3://kyoungsu-aws-logs-icn/emr/"]
    },
    {
        "Name":"SparkSubmit",
        "ActionOnFailure":"CONTINUE",
        "Type":"CUSTOM_JAR",
        "Jar":"command-runner.jar",
        "Args":["spark-submit", "--deploy-mode", "cluster", "--master", "yarn", "-v", "--conf", "spark.executor.memory='"${EXECUTOR_MEMORY}"'", "--conf", "spark.driver.memory='"${DRIVER_MEMORY}"'", "--conf", "spark.driver.cores='"${DRIVER_CORES}"'", "s3://awsdemo-ap-northeast-2/aws-blog-spark-parquet-conversion/convert2parquet.py","-d","OUTPUT=s3://kyoungsu-aws-logs-icn/emr/"]
    },
    {
        "Name":"S3DistCP",
        "ActionOnFailure":"CONTINUE",
        "Type":"CUSTOM_JAR",
        "Jar":"command-runner.jar",
        "Args":["s3-dist-cp", "--s3Endpoint=s3.ap-northeast-2.amazonaws.com", "--src=hdfs:///user/hadoop/elblogs_pq/", "--dest=s3://awsdemo-ap-northeast-2/aws-blog-spark-parquet-conversion/converted-'"${CLUSTER_NAME}"'"]
    }
]'
`
./create-rule.sh "${CLUSTER_ID}"
