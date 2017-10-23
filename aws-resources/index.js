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
      var regionName = data.Regions[i].RegionName;
      AWS.config.update({region: regionName});
      ec2 = new AWS.EC2();
      getInstance(ec2, regionName);

      rds = new AWS.RDS();
      getRds(rds, regionName);

      redshift = new AWS.Redshift();
      getRedshift(redshift, regionName);

      dynamodb = new AWS.DynamoDB();
      getDynamoDB(dynamodb, regionName);

      directoryservice = new AWS.DirectoryService();
      getDirectoryService(directoryservice, regionName);


      var elasticache = new AWS.ElastiCache();
      getElasticache(elasticache, regionName);

      var elb = new AWS.ELB();
      getELB(elb, regionName);

      var elbv2 = new AWS.ELBv2();
      getELBv2(elbv2, regionName);

    }
  }
});


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
          console.log(region, d.Stage, d.DirectoryId, d.Type + '-' + d.Size, d.VpcSettings.VpcID, d.VpcSettings.SubnetIds, d.Name, d.LaunchTime, d.AccessUrl, d.ShortName);
        
        }
      }
    });    
  }
  catch(err) {

  } 
}


function getNameTag(item) {
  if(undefined != item.Tags && undefined != item.Tags['Name']) {
    return item.Tags['Name'].Value;
  } else
    return "NoName";
}

function getElasticache(client, region) {
  var params = {}
  client.describeReplicationGroups(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else {
      console.log(data);
      for(var i =0; i<data.ReplicationGroups.length; i++) {
        var r = data.ReplicationGroups[i];
        console.log(r);
        console.log(region, r.Status, r.ReplicationGroupId, r.CacheNodeType, 'instance.ImageId', 'instance.VpcId', 'instance.SubnetId', getNameTag(r), getEndpointUrl(r.ConfigurationEndpoint), 'instance.LaunchTime', r.MemberClusters.length);
      }
    }
  });
  
}


   /*
   data = {
    LoadBalancerDescriptions: [
       {
      AvailabilityZones: [
         "us-west-2a"
      ], 
      BackendServerDescriptions: [
         {
        InstancePort: 80, 
        PolicyNames: [
           "my-ProxyProtocol-policy"
        ]
       }
      ], 
      CanonicalHostedZoneName: "my-load-balancer-1234567890.us-west-2.elb.amazonaws.com", 
      CanonicalHostedZoneNameID: "Z3DZXE0EXAMPLE", 
      CreatedTime: <Date Representation>, 
      DNSName: "my-load-balancer-1234567890.us-west-2.elb.amazonaws.com", 
      HealthCheck: {
       HealthyThreshold: 2, 
       Interval: 30, 
       Target: "HTTP:80/png", 
       Timeout: 3, 
       UnhealthyThreshold: 2
      }, 
      Instances: [
         {
        InstanceId: "i-207d9717"
       }, 
         {
        InstanceId: "i-afefb49b"
       }
      ], 
      ListenerDescriptions: [
         {
        Listener: {
         InstancePort: 80, 
         InstanceProtocol: "HTTP", 
         LoadBalancerPort: 80, 
         Protocol: "HTTP"
        }, 
        PolicyNames: [
        ]
       }, 
         {
        Listener: {
         InstancePort: 443, 
         InstanceProtocol: "HTTPS", 
         LoadBalancerPort: 443, 
         Protocol: "HTTPS", 
         SSLCertificateId: "arn:aws:iam::123456789012:server-certificate/my-server-cert"
        }, 
        PolicyNames: [
           "ELBSecurityPolicy-2015-03"
        ]
       }
      ], 
      LoadBalancerName: "my-load-balancer", 
      Policies: {
       AppCookieStickinessPolicies: [
       ], 
       LBCookieStickinessPolicies: [
          {
         CookieExpirationPeriod: 60, 
         PolicyName: "my-duration-cookie-policy"
        }
       ], 
       OtherPolicies: [
          "my-PublicKey-policy", 
          "my-authentication-policy", 
          "my-SSLNegotiation-policy", 
          "my-ProxyProtocol-policy", 
          "ELBSecurityPolicy-2015-03"
       ]
      }, 
      Scheme: "internet-facing", 
      SecurityGroups: [
         "sg-a61988c3"
      ], 
      SourceSecurityGroup: {
       GroupName: "my-elb-sg", 
       OwnerAlias: "123456789012"
      }, 
      Subnets: [
         "subnet-15aaab61"
      ], 
      VPCId: "vpc-a01106c2"
     }
    ]
   }
   */


function getELB(client, region) {
  var params = {}
  client.describeLoadBalancers(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else {
      console.log(data);
      for(var i =0; i<data.LoadBalancerDescriptions.length; i++) {
        var r = data.LoadBalancerDescriptions[i];
        console.log(r);
        console.log(region, "r.Status", r.DNSName, r.Scheme, 'instance.ImageId', r.VpcId, r.Subnets, getNameTag(r), 'getEndpointUrl(r.ConfigurationEndpoint)', r.CreatedTime, r.Instances.length);
      }
    }
  });
  
}


function getELBv2(client, region) {
  var params = {}
  client.describeLoadBalancers(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else {
      console.log(data);
      for(var i =0; i<data.LoadBalancers.length; i++) {
        var r = data.LoadBalancers[i];
        console.log(r);
        console.log(region, r.State.code, r.DNSName, r.Type, 'instance.ImageId', r.VpcId, r.Subnets, getNameTag(r), 'getEndpointUrl(r.ConfigurationEndpoint)', r.CreatedTime, (undefined != r.Instance)? r.Instances.length: 0);
      }
    }
  });
  
}