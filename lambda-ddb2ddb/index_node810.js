'use strict';
var AWS = require("aws-sdk");

// Create the DynamoDB service object
var ddb = new AWS.DynamoDB();
const TABLE_NAME = "lookup_synced";
console.log('Loading function');

exports.handler = async (event, context) => {
    console.log('Received event:', JSON.stringify(event, null, 2));
    var params = {
        TableName: TABLE_NAME
    };
    await ddb.describeTable(params)
    .promise()
    .then(function(data) {
        console.log(JSON.stringify(data));
    })
    .catch(function(err){
        console.log(err, err.stack); // an error occurred
    })
    params = {
        RequestItems: {}
                
    };
    params.RequestItems[TABLE_NAME] = new Array();
    
    var completed = false;  
    event.Records.forEach((record) => {
        console.log(record.dynamodb.NewImage);
        var item;
        if (record.eventName == "INSERT" || record.eventName == "MODIFY") { 
            item = {
                PutRequest:{
                    Item: record.dynamodb.NewImage
                }};

            item.PutRequest.Item.action = {"S": "PutRequest"}   
            
            
        } else if(record.eventName == 'REMOVE') {
            item = { 
                PutRequest: {
                    Item: record.dynamodb.OldImage }}
                item.PutRequest.Item.action = {"S": "DeleteRequest"}
        }
        item.PutRequest.Item.requested_dt = {"N":"" + new Date().getTime()};
        

        params.RequestItems[TABLE_NAME].push( item);
            
        
        console.log(record.eventID);
        console.log(record.eventName);
        console.log('DynamoDB Record: %j', record.dynamodb);
    });
    console.log(JSON.stringify(params));
            
    
    await ddb.batchWriteItem(params)
        .promise()
        .then(function(data){
            console.log(JSON.stringify(data));
        }).catch(function(err){
            console.log(err);
        })
};
