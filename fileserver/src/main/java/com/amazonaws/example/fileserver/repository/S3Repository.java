package com.amazonaws.example.fileserver.repository;

import java.io.InputStream;
import java.util.List;

import com.amazonaws.services.s3.model.*;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import com.amazonaws.services.s3.AmazonS3;

@Repository
public class S3Repository {
	private static final Log log = LogFactory.getLog(S3Repository.class);

	@Autowired
	private AmazonS3 amazonS3;

	public String store(String bucket, String objectKey, InputStream inputStream) {

		ObjectMetadata objectMetadata = new ObjectMetadata();
		PutObjectResult requestResult = amazonS3.putObject(bucket, objectKey, inputStream, objectMetadata);
		return requestResult.getETag();
	}

	//https://docs.aws.amazon.com/ko_kr/sdk-for-java/v1/developer-guide/examples-s3-objects.html#download-object
	public S3Object getObject(String bucket, String objectKey) {
		return amazonS3.getObject(bucket, objectKey);

	}
	public List<S3ObjectSummary> objectList(String bucket) {
		return amazonS3.listObjectsV2(bucket).getObjectSummaries();
	}

	public void delete(String bucket, String objectKey) {
		amazonS3.deleteObject(bucket, objectKey);
	}
}
