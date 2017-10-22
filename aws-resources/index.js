var AWS = require('aws-sdk');

AWS.config.update({region: 'ap-northeast-2'});
var s3 = new AWS.S3();
var ec2 = new AWS.EC2();

var params = { };

var regionNames =[];
ec2.describeRegions(params, function(err, data) {
  if (err) console.log(err, err.stack); // an error occurred
  else {
    for(var i=0;i<data.Regions.length;i++) {
      AWS.config.update({region: data.Regions[i].RegionName});
      ec2 = new AWS.EC2();
      getInstance(ec2, data.Regions[i].RegionName);

      rds = new AWS.RDS();
      getRds(rds, data.Regions[i].RegionName);

      redshift = new AWS.Redshift();
      getRedshift(redshift, data.Regions[i].RegionName);

      dynamodb = new AWS.DynamoDB();
      getDynamoDB(dynamodb, data.Regions[i].RegionName);

      directoryservice = new AWS.DirectoryService();
      getDirectoryService(directoryservice, data.Regions[i].RegionName);

    }
  }
});

// 버킷 이름은 모든 S3 사용자에게 고유한 것이어야 합니다.
/*

{ AmiLaunchIndex: 0,
  ImageId: 'ami-6869aa05',
  InstanceId: 'i-dc190842',
  InstanceType: 't2.medium',
  KeyName: 'CODE-DEPLOY-VIR',
  LaunchTime: 2016-08-16T03:57:41.000Z,
  Monitoring: { State: 'disabled' },
  Placement:
   { AvailabilityZone: 'us-east-1b',
     GroupName: '',
     Tenancy: 'default' },
  PrivateDnsName: 'ip-10-0-2-181.ec2.internal',
  PrivateIpAddress: '10.0.2.181',
  ProductCodes: [],
  PublicDnsName: 'ec2-52-205-27-31.compute-1.amazonaws.com',
  PublicIpAddress: '52.205.27.31',
  State: { Code: 16, Name: 'running' },
  StateTransitionReason: '',
  SubnetId: 'subnet-d175d7fb',
  VpcId: 'vpc-e084b184',
  Architecture: 'x86_64',
  BlockDeviceMappings: [ { DeviceName: '/dev/xvda', Ebs: [Object] } ],
  ClientToken: 'bxbak1471319860756',
  EbsOptimized: false,
  EnaSupport: true,
  Hypervisor: 'xen',
  ElasticGpuAssociations: [],
  NetworkInterfaces:
   [ { Association: [Object],
       Attachment: [Object],
       Description: 'Primary network interface',
       Groups: [Object],
       Ipv6Addresses: [],
       MacAddress: '12:70:91:24:f0:75',
       NetworkInterfaceId: 'eni-b604b1a6',
       OwnerId: '519590242672',
       PrivateDnsName: 'ip-10-0-2-181.ec2.internal',
       PrivateIpAddress: '10.0.2.181',
       PrivateIpAddresses: [Object],
       SourceDestCheck: true,
       Status: 'in-use',
       SubnetId: 'subnet-d175d7fb',
       VpcId: 'vpc-e084b184' } ],
  RootDeviceName: '/dev/xvda',
  RootDeviceType: 'ebs',
  SecurityGroups: [ { GroupName: 'VIRJenkins', GroupId: 'sg-51ea2b2b' } ],
  SourceDestCheck: true,
  Tags: [ { Key: 'Name', Value: 'Jenkins' } ],
  VirtualizationType: 'hvm' }
*/



function getInstance(EC2Client, region) {
  var params = {}
  EC2Client.describeInstances(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else {
      for(var i =0; i<data.Reservations.length; i++) {
        var instance = data.Reservations[i].Instances[0];
        console.log(region, instance.State.Name, instance.InstanceId, instance.InstanceType, instance.ImageId, instance.VpcId, instance.SubnetId, (instance.Tags['Name'] == undefined)?'NoName': instance.Tags['Name'].Value, instance.PublicDnsName, instance.LaunchTime);
      }
    }
  });
  EC2Client.describeVolumes(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else {
      for(var i =0; i<data.Volumes.length; i++) {
        var volume = data.Volumes[i];
        console.log(region, volume.State, volume.VolumeId, volume.VolumeType, volume.SnapshotId, 'VpcId', volume.AvailabilityZone, (volume.Tags['Name'] == undefined)?'NoName': volume.Tags['Name'].Value, 'instance.PublicDnsName', volume.CreateTime);
      }
    }
  });
}

/*
{ ResponseMetadata: { RequestId: 'd33d980d-b6e3-11e7-adc3-a9a8990abb76' },
  DBInstances:
   [ { DBInstanceIdentifier: 'testdbicn',
       DBInstanceClass: 'db.t2.medium',
       Engine: 'aurora',
       DBInstanceStatus: 'available',
       MasterUsername: 'testdb',
       DBName: 'testdb',
       Endpoint: [Object],
       AllocatedStorage: 1,
       InstanceCreateTime: 2017-10-08T01:34:52.407Z,
       PreferredBackupWindow: '18:31-19:01',
       BackupRetentionPeriod: 1,
       DBSecurityGroups: [],
       VpcSecurityGroups: [Object],
       DBParameterGroups: [Object],
       AvailabilityZone: 'ap-northeast-2a',
       DBSubnetGroup: [Object],
       PreferredMaintenanceWindow: 'sun:15:12-sun:15:42',
       PendingModifiedValues: {},
       MultiAZ: false,
       EngineVersion: '5.6.10a',
       AutoMinorVersionUpgrade: true,
       ReadReplicaDBInstanceIdentifiers: [],
       ReadReplicaDBClusterIdentifiers: [],
       LicenseModel: 'general-public-license',
       OptionGroupMemberships: [Object],
       PubliclyAccessible: true,
       StatusInfos: [],
       StorageType: 'aurora',
       DbInstancePort: 0,
       DBClusterIdentifier: 'testdb',
       StorageEncrypted: false,
       DbiResourceId: 'db-RPDBBJNRNFSERZHJTIIDAKXOJU',
       CACertificateIdentifier: 'rds-ca-2015',
       DomainMemberships: [],
       CopyTagsToSnapshot: false,
       MonitoringInterval: 1,
       EnhancedMonitoringResourceArn: 'arn:aws:logs:ap-northeast-2:519590242672:log-group:RDSOSMetrics:log-stream:db-RPDBBJNRNFSERZHJTIIDAKXOJU',
       MonitoringRoleArn: 'arn:aws:iam::519590242672:role/rds-monitoring-role',
       PromotionTier: 0,
       DBInstanceArn: 'arn:aws:rds:ap-northeast-2:519590242672:db:testdbicn',
       IAMDatabaseAuthenticationEnabled: false,
       PerformanceInsightsEnabled: false },


       [ { VpcSecurityGroupId: 'sg-9d9f8be2', Status: 'active' } ] { DBSubnetGroupName: 'awseb-e-dbrejn3dze-stack-awsebrdsdbsubnetgroup-xv9v987pvpbo',
  DBSubnetGroupDescription: 'RDS DB Subnet Group',
  VpcId: 'vpc-66f38e00',
  SubnetGroupStatus: 'Complete',
  Subnets:
   [ { SubnetIdentifier: 'subnet-a280a28f',
       SubnetAvailabilityZone: [Object],
       SubnetStatus: 'Active' },
     { SubnetIdentifier: 'subnet-c40f1d8d',
       SubnetAvailabilityZone: [Object],
       SubnetStatus: 'Active' } ] } benchmark { Address: 'benchmark.cy9qmlpgp8dr.us-east-1.rds.amazonaws.com',
  Port: 3306,
  HostedZoneId: 'Z2R2ITUGPM61AM' }
*/
function getRds(RDSClient, region) {
 var params = {}
  RDSClient.describeDBInstances(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else {
      for(var i =0; i<data.DBInstances.length; i++) {
        var instance = data.DBInstances[i];
        console.log(region, instance.DBInstanceStatus, instance.DbiResourceId, instance.DBInstanceClass, instance.Engine + "/" + instance.EngineVersion, instance.DBSubnetGroup.VpcId, instance.DBSubnetGroup.Subnets[0].SubnetIdentifier, instance.DBInstanceIdentifier, instance.Endpoint.Address + ":" + instance.Endpoint.Port, instance.InstanceCreateTime);
      }
    }
  }); 
}


/*

{ ResponseMetadata: { RequestId: '2a2a5f3d-b6e7-11e7-8845-f197f8afa762' },
  Clusters:
   [ { ClusterIdentifier: 'redshift-1',
       NodeType: 'dc2.large',
       ClusterStatus: 'creating',
       MasterUsername: 'yikster',
       DBName: 'redshift1',
       AutomatedSnapshotRetentionPeriod: 1,
       ClusterSecurityGroups: [],
       VpcSecurityGroups: [Object],
       ClusterParameterGroups: [Object],
       ClusterSubnetGroupName: 'default',
       VpcId: 'vpc-6c34d505',
       PreferredMaintenanceWindow: 'sat:13:30-sat:14:00',
       PendingModifiedValues: [Object],
       ClusterVersion: '1.0',
       AllowVersionUpgrade: true,
       NumberOfNodes: 2,
       PubliclyAccessible: true,
       Encrypted: false,
       ClusterNodes: [Object],
       ClusterRevisionNumber: '1497',
       Tags: [],
       EnhancedVpcRouting: false,
       IamRoles: [] } ] }

*/

function getEndpointUrl(endpoint) {
  var url = "undefined";
  var port = "undefined";

  if(undefined != endpoint) {
    if(undefined != endpoint.Address)
      url = endpoint.Address

    if(undefined != endpoint.Port)
      port = endpoint.Port;  
  }
  

  return url + ":" + port;

}
function getRedshift(client, region) {
 var params = {}
  client.describeClusters(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else {
      for(var i =0; i<data.Clusters.length; i++) {
        var instance = data.Clusters[i];
        console.log(region, instance.ClusterStatus, instance.ClusterIdentifier, instance.NodeType, instance.ClusterVersion, instance.VpcId, instance.ClusterSubnetGroupName, 'instance.DBInstanceIdentifier', getEndpointUrl(instance.Endpoint));
      }
    }
  }); 
}

/*

{ Table:
   { AttributeDefinitions: [ [Object] ],
     TableName: 'StartupKitServerlessTodoApp-Table-1NBCU2ILJ9HW7',
     KeySchema: [ [Object] ],
     TableStatus: 'ACTIVE',
     CreationDateTime: 2017-09-20T05:49:46.630Z,
     ProvisionedThroughput:
      { NumberOfDecreasesToday: 0,
        ReadCapacityUnits: 100,
        WriteCapacityUnits: 100 },
     TableSizeBytes: 0,
     ItemCount: 0,
     TableArn: 'arn:aws:dynamodb:us-east-1:519590242672:table/StartupKitServerlessTodoApp-Table-1NBCU2ILJ9HW7' } }

*/

function getProvisions(p) {
  return p.ReadCapacityUnits + "RCU," + p.WriteCapacityUnits + "WCU";
}
function getDynamoDB(client, region) {
 var params = {}
  client.listTables(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else {
      // console.log(data);
      for(var i =0; i<data.TableNames.length; i++) {
        var tableParam = {TableName: data.TableNames[i]};
        client.describeTable(tableParam, function(errTable, dataTable){
          if (errTable) console.log(errTable, errTable.stack); // an error occurred
          else {
            var t = dataTable.Table;
            console.log(region, t.TableStatus, t.TableName, getProvisions(t.ProvisionedThroughput), t.CreationDataTime);
          }
    });
        
      }
    }
  });  
}

/*

{ DirectoryId: 'd-90672bfb59',
       Name: 'msad.yikster.net',
       ShortName: 'CORP',
       Size: 'Large',
       Alias: 'd-90672bfb59',
       AccessUrl: 'd-90672bfb59.awsapps.com',
       DnsIpAddrs: [Object],
       Stage: 'Active',
       LaunchTime: 2017-10-22T10:37:48.222Z,
       StageLastUpdatedDateTime: 2017-10-22T11:02:12.150Z,
       Type: 'MicrosoftAD',
       VpcSettings: [Object],
       SsoEnabled: false,
       DesiredNumberOfDomainControllers: 2 },

*/

function getDirectoryService(client, region) {
 var params = {}
  try {
    client.describeDirectories(params, function(err, data) {
      if (err) {
        // console.log(err.code);
        if(undefined != err.code && 'UnknownEndpoint' == err.code) {
          console.log(region, 'Not Support DirectoryService');
        } else {
          console.log(err, err.stack); // an error occurred
        }
      }
      else {
        //console.log(data);
        for(var i =0; i<data.DirectoryDescriptions.length; i++) {
          var d = data.DirectoryDescriptions[i];
          console.log(region, d.State, d.DirectoryId, d.Type + '-' + d.Size, d.VpcSettings.VpcID, d.VpcSettings.SubnetIds, d.Name, d.LaunchTime, d.AccessUrl, d.ShortName);
        
        }
      }
    });    
  }
  catch(err) {

  } 
}