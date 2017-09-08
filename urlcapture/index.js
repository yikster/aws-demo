var scrapper = require('./scraper');
const path = require('path');
const fs = require('fs');
const AWS = require('aws-sdk');

exports.handler = function(event, context, callback) {
  if (event.url) {
    scrapper.scrape(event.url, function(err, result) {
      if (err) {
        return callback(null, {error: result});
      }
      console.log(result);
      var imageBuffer = new Buffer(result, 'BASE64');
//      console.log(imageBufer);
      //fs.createReadStream("aaa.png");
/*
      const tmp_file_path = path.join(__dirname, 'aaa.png');
       const params = {Bucket: 'bucketName', Key: 'screen/aaa.png', 
         Body: fs.createReadStream(tmp_file_path),};
         new AWS.S3().upload(params, (error, data) => {
           callback(error, 'fin!!');
       });
*/
      callback(null, {result: result});
    })
  }
  else {
    callback(null, {error: 'bad query'});
  }
};
