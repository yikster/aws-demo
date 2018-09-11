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
	
	@Value("${amazon.dynamodb.endpoint}")
	private String amazonDynamoDBEndpoint;

	@Value("${amazon.aws.accesskey}")
	private String amazonAWSAccessKey;

	@Value("${amazon.aws.secretkey}")
	private String amazonAWSSecretKey;

	@Value("${amazon.aws.s3.accesskey}")
	private String amazonAWSS3AccessKey;

	@Value("${amazon.aws.s3.secretkey}")
	private String amazonAWSS3SecretKey;

	@Value("${amazon.dynamodb.region}")
	private String dynamodbRegion;

	@Value("${amazon.dynamodb.tablename}")
	private String tableName;
	
	@Value("${amazon.aws.s3.region}")
	private String s3RegionName;

	@Bean
	public DynamoDBMapper dynamoDBMapper() {
		return new DynamoDBMapper(amazonDynamoDB());
	}

	@Bean
	public AmazonS3 amazonS3() {
		AmazonS3 client = null;
		AmazonS3ClientBuilder builder = null;;

		// if no credential information is set in the properties file do nothing
		if (StringUtils.isEmpty(amazonAWSS3AccessKey) || StringUtils.isEmpty(amazonAWSS3SecretKey)) {
			builder = AmazonS3ClientBuilder.standard();
			// if credential information is set, use it
		} else {
			BasicAWSCredentials awsCreds = new BasicAWSCredentials(amazonAWSS3AccessKey, amazonAWSS3SecretKey);
			builder = AmazonS3ClientBuilder.standard().withCredentials(new AWSStaticCredentialsProvider(awsCreds));
		}

		builder.setRegion(s3RegionName);
		client = builder.build();

		return client;
	}


	@Bean
	public AmazonDynamoDB amazonDynamoDB() {
		AmazonDynamoDB client = null;
		AmazonDynamoDBClientBuilder builder = null;

		// if no credential information is set in the properties file do nothing
		if (StringUtils.isEmpty(amazonAWSAccessKey) || StringUtils.isEmpty(amazonAWSSecretKey)) {
			builder = AmazonDynamoDBClientBuilder.standard();
			// if credential information is set, use it
		} else {
			BasicAWSCredentials awsCreds = new BasicAWSCredentials(amazonAWSAccessKey, amazonAWSSecretKey);
			builder = AmazonDynamoDBClientBuilder.standard().withCredentials(new AWSStaticCredentialsProvider(awsCreds));
		}
		System.out.println("Region:" + dynamodbRegion);
		client = builder.withRegion(dynamodbRegion).build();
		
		// if endpoint is set for local dynamodb
		if (!StringUtils.isEmpty(amazonDynamoDBEndpoint)) {
			client.setEndpoint(amazonDynamoDBEndpoint);
		}

		return client;
	}

}
