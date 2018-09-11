package com.amazonaws.example.fileserver.repository;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.amazonaws.example.fileserver.model.FileInfo;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBQueryExpression;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBScanExpression;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;

@Repository
public class DDBRepositoryImpl implements DDBRepository {
	private static final Log log = LogFactory.getLog(DDBRepositoryImpl.class);

	@Autowired
	private DynamoDBMapper mapper;



	@Override
	public void addNewFileRecord(FileInfo fileInfo) {
		mapper.save(fileInfo);

	}
	@Override
	public List<FileInfo> getByGuid(String guid) {

		Map<String, AttributeValue> eav = new HashMap();
		eav.put(":v1", new AttributeValue().withS(guid));

		DynamoDBQueryExpression<FileInfo> queryExpression = new DynamoDBQueryExpression<FileInfo>()
				.withKeyConditionExpression("guid = :v1").withExpressionAttributeValues(eav);

		List<FileInfo> list = mapper.query(FileInfo.class, queryExpression);
		return list;
	}



	@Override
	public List<FileInfo> scan() {

		return mapper.scan(FileInfo.class, new DynamoDBScanExpression());
	}

}
