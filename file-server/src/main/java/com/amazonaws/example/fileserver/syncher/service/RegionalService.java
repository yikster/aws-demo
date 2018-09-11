package com.amazonaws.example.fileserver.syncher.service;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.example.fileserver.repository.S3Repository;
import com.amazonaws.example.fileserver.syncher.processor.OutboundProcessorFactory;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.cloudwatch.AmazonCloudWatch;
import com.amazonaws.services.cloudwatch.AmazonCloudWatchClientBuilder;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClient;
import com.amazonaws.services.dynamodbv2.model.DescribeTableResult;
import com.amazonaws.services.dynamodbv2.streamsadapter.AmazonDynamoDBStreamsAdapterClient;
import com.amazonaws.services.dynamodbv2.streamsadapter.StreamsWorkerFactory;
import com.amazonaws.services.kinesis.clientlibrary.lib.worker.InitialPositionInStream;
import com.amazonaws.services.kinesis.clientlibrary.lib.worker.KinesisClientLibConfiguration;
import com.amazonaws.services.kinesis.clientlibrary.lib.worker.Worker;

@Service
public class RegionalService implements DataSyncService {
	private static final Log log = LogFactory.getLog(RegionalService.class);

	@Autowired
	private AmazonDynamoDBClient dynamoDBClient;

	@Autowired
	private S3Repository s3Repository;

	@Value("${amazon.dynamodb.tablename}")
	private String tableName;

	private ExecutorService workerThread;

	@Override
	public void startPuller() {
		
	}

	@Override
	public void startPusher() {


		AWSCredentialsProvider awsCredentialsProvider = new DefaultAWSCredentialsProviderChain();


		new DefaultAWSCredentialsProviderChain().getCredentials();new ProfileCredentialsProvider();
		OutboundProcessorFactory outboundProcessorFactory = new OutboundProcessorFactory(s3Repository);

		DescribeTableResult describeTableResult = dynamoDBClient.describeTable(tableName);
		String streamArn = describeTableResult.getTable().getLatestStreamArn();


		AmazonDynamoDBStreamsAdapterClient adapterClient = new AmazonDynamoDBStreamsAdapterClient(awsCredentialsProvider,
				dynamoDBClient.getClientConfiguration());
		adapterClient.setRegion(Region.getRegion(Regions.AP_NORTHEAST_2));

		String workerId = null;
		try {
			workerId = InetAddress.getLocalHost().getCanonicalHostName() + ":" + UUID.randomUUID();
		} catch (UnknownHostException e) {
			// TODO Auto-generated catch block
			log.error(e);
		}

		KinesisClientLibConfiguration workerConfig = new KinesisClientLibConfiguration("LookupDataStreamHandler",
				streamArn, awsCredentialsProvider, workerId).withMaxRecords(1000).withIdleTimeBetweenReadsInMillis(500)
						.withInitialPositionInStream(InitialPositionInStream.TRIM_HORIZON);

		log.info("Creating worker for stream: " + streamArn);

		AmazonCloudWatch cloudWatchClient = AmazonCloudWatchClientBuilder.standard().build();

		Worker worker = StreamsWorkerFactory.createDynamoDbStreamsWorker(outboundProcessorFactory, workerConfig,
				adapterClient, dynamoDBClient, cloudWatchClient);

		workerThread = Executors.newSingleThreadExecutor();
		workerThread.submit(worker);

		log.info("Starting worker...");

		// commenting the below line out as this is currently in the form of web
		// service. For a prod batch application, the below line needs to be
		// uncommented.
		// workerThread.shutdown(); //This will wait till the KCL worker exits		
	}

	@Override
	public void push() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void pull() {
		// TODO Auto-generated method stub
		
	}
	
}
