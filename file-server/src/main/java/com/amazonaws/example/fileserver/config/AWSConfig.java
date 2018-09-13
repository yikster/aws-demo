package com.amazonaws.example.fileserver.config;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.UUID;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.util.StringUtils;

import com.amazonaws.AmazonClientException;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBStreams;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBStreamsClientBuilder;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.kinesis.clientlibrary.lib.worker.InitialPositionInStream;
import com.amazonaws.services.kinesis.clientlibrary.lib.worker.KinesisClientLibConfiguration;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;

@Configuration
public class AWSConfig {
	
	private static final Log log = LogFactory.getLog(AWSConfig.class);
	
	@Bean
	public DynamoDBMapper dynamoDBMapper() {
		return new DynamoDBMapper(amazonDynamoDB());
	}

	@Bean
	public AmazonS3 amazonS3() {
		return AmazonS3ClientBuilder.standard().build();
	}


	@Bean
	public AmazonDynamoDB amazonDynamoDB() {
		return AmazonDynamoDBClientBuilder.standard().build();
	}

}
