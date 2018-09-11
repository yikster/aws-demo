package com.amazon.aws;

import com.amazonaws.example.fileserver.controller.LookupDataController;
import com.amazonaws.example.fileserver.repository.DDBRepositoryImpl;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import org.junit.Ignore;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;

//@RunWith(SpringRunner.class)
//@SpringBootTest(classes = LookupDataController.class)
//@ComponentScan("com.amazon.aws.prototype.lookup.syncher")
//@Import({DDBRepositoryImpl.class})
@Ignore
public class DynamodbInboundSynchronizerApplicationTests {


	@Autowired
	LookupDataController lookupDataController;

	@Autowired
	DDBRepositoryImpl ddbRepository;

	@Autowired
	private DynamoDBMapper mapper;

	@Test
	public void contextLoads() {
		AmazonDynamoDBClientBuilder
				.standard().withRegion("eu-central-1").build()
				.listTables().getTableNames().forEach( (v) ->{
			System.out.println(v);
		});

		lookupDataController.scan();

		lookupDataController.putItem();

	}
}
