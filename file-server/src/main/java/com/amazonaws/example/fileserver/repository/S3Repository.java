package com.amazonaws.example.fileserver.repository;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;

import com.amazonaws.services.s3.model.*;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;
import org.springframework.util.StreamUtils;

import com.amazonaws.services.s3.AmazonS3;
import org.springframework.web.multipart.MultipartFile;

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

	public List<S3ObjectSummary> objectList(String bucket) {
		return amazonS3.listObjectsV2(bucket).getObjectSummaries();
	}

}
