package com.amazonaws.example.fileserver.repository;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.amazonaws.example.fileserver.model.FileInfo;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Repository;

import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBQueryExpression;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBScanExpression;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;

@Component("ddbRepository")
public class DDBRepository {
	private static final Log log = LogFactory.getLog(DDBRepository.class);

	@Autowired
	private DynamoDBMapper mapper;

	public void addNewFileRecord(FileInfo fileInfo) {
//		if(null == fileInfo.getCreatedAt() || 0 == fileInfo.getCreatedAt())
		fileInfo.setCreatedAt(System.currentTimeMillis());
		mapper.save(fileInfo);

	}

	public FileInfo getByGuid(String guid) {

		Map<String, AttributeValue> eav = new HashMap<>();

		eav.put(":v1", new AttributeValue().withS(guid));

		DynamoDBQueryExpression<FileInfo> queryExpression = new DynamoDBQueryExpression<FileInfo>()
				.withKeyConditionExpression("guid = :v1").withExpressionAttributeValues(eav);

		List<FileInfo> list = mapper.query(FileInfo.class, queryExpression);
		if(1 == list.size())
			return list.get(0);

		return null;
	}

	public List<FileInfo> scan() {

		return mapper.scan(FileInfo.class, new DynamoDBScanExpression());
	}

	public void deleteOne(String guid) {
		FileInfo fileInfo = getByGuid(guid);
		log.info("Find file:" + fileInfo);
		if(null != fileInfo) {
			deleteOne(fileInfo);
		}
	}

	public void deleteOne(FileInfo fileInfo) {
		mapper.delete(fileInfo);
	}
}
