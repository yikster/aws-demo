// Load the AWS SDK for Node.js
var AWS = require('aws-sdk');
// Set the region 
AWS.config.update({region: 'REGION'});

// Create an SQS service object
var sqs = new AWS.SQS({apiVersion: '2012-11-05'});

var queueURL = "https://sqs.ap-northeast-2.amazonaws.com/174548683514/NewFiles";

var params = {
 AttributeNames: [
    "SentTimestamp"
 ],
 MaxNumberOfMessages: 10,
 MessageAttributeNames: [
    "All"
 ],
 QueueUrl: queueURL,
 VisibilityTimeout: 20,
 WaitTimeSeconds: 1
};


function getMessages() {
  console.log("waiting :" + new Date())
  sqs.receiveMessage(params, function(err, data) {
    if (err) {
      console.log("Receive Error", err);
    } else if (data.Messages) {
      console.log(JSON.stringify(data))
      for(let message of data.Messages) {
        console.log("key:" + message.Body.Records)
        //[0].s3.object.key)
        var deleteParams = {
          QueueUrl: queueURL,
          ReceiptHandle: message.ReceiptHandle
        };
        sqs.deleteMessage(deleteParams, function(err, data) {
          if (err) {
            console.log("Delete Error", err);
          } else {
            console.log("Message Deleted", data);
          }
        });
      }
    }
  });
  setTimeout( getMessages, 1000);
}

setTimeout( getMessages, 1000);
/*

while(true) {

}
*/