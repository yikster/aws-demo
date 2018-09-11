package com.amazonaws.example.fileserver.syncher.processor;

import com.amazonaws.example.fileserver.repository.S3Repository;
import com.amazonaws.services.kinesis.clientlibrary.interfaces.v2.IRecordProcessor;
import com.amazonaws.services.kinesis.clientlibrary.interfaces.v2.IRecordProcessorFactory;

public class OutboundProcessorFactory implements IRecordProcessorFactory {
	
	private S3Repository s3Repository;
	
    public OutboundProcessorFactory(S3Repository s3Repository) {
    	this.s3Repository = s3Repository;
    }

    @Override
    public IRecordProcessor createProcessor() {
        return new OutboundProcessor(s3Repository);
    }
}