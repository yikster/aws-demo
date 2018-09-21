package com.amazonaws.example.fileserver.model;


import com.amazonaws.services.dynamodbv2.datamodeling.*;

@DynamoDBTable(tableName = "FileInfo")
public class FileInfo {
    private String guid;
    private String bucket;
    private String objectKey;
    private String filePath;
    private Long size;
    private Long createdAt;

    public FileInfo() {
    }

    public FileInfo(String bucket, String objectKey) {
        this.bucket = bucket;
        this.objectKey = objectKey;
    }

    public FileInfo(String bucket, String objectKey, long size) {
        this.bucket = bucket;
        this.objectKey = objectKey;
        this.size = size;
    }

    public FileInfo(String guid, Long createdAt) {
        this.guid = guid;
        this.createdAt = createdAt;
    }

    public FileInfo(String guid, String bucket, String objectKey, String filePath, long size) {
        this.guid = guid;
        this.bucket = bucket;
        this.objectKey = objectKey;
        this.size = size;
        this.filePath = filePath;
    }

    @DynamoDBHashKey(attributeName = "guid")
    public String getGuid() {
        return guid;
    }
    public void setGuid(String guid) {
        this.guid = guid;
    }


    @DynamoDBAttribute
    public String getBucket() {
        return bucket;
    }
    public void setBucket(String bucket) {
        this.bucket = bucket;
    }

    @DynamoDBAttribute
    public String getObjectKey() {
        return objectKey;
    }
    public void setObjectKey(String objectKey) {
        this.objectKey = objectKey;
    }

    @DynamoDBAttribute
    public Long getSize() { return size; }
    public void setSize(Long size) {
        this.size = size;
    }

    @DynamoDBAttribute
    public String getFilePath() { return filePath; }
    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }

    @DynamoDBRangeKey(attributeName = "createdAt")
    public Long getCreatedAt() { return createdAt; }
    public void setCreatedAt(Long creatdAt) {this.createdAt = creatdAt; }


    @Override
    public String toString() {
        return "FileInfo{" +
                "guid='" + guid + '\'' +
                ", bucket='" + bucket + '\'' +
                ", objectKey='" + objectKey + '\'' +
                ", size=" + size +
                ", createdAt=" + createdAt +
                '}';
    }
}
