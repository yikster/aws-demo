'use strict';

var readline = require('readline');
var fs = require('fs');
var SQL_TEXT_FILE = process.argv[2];

var reader = readline.createInterface({
  input: fs.createReadStream(SQL_TEXT_FILE)
});

var linenumber = 1;
console.log('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd"><mapper namespace="com.aws.sct.example">');
reader.on('line', function (line) {
	line = line.replace(/\s\s+/g, ' ');
        if(line.endsWith(", ")) {
            line = line.replace(/\:[1-9][0-9][0-9] , /g, '') + ':101 )'
        }
	console.log('<select id=ext_sql_id_"' + linenumber++ + '" >' + line + '</select>');
}).on('close', function(line) {
	console.log('</mapper></xml>');
});



