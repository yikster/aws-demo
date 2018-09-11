package com.amazonaws.example.fileserver.syncher.processor;

import java.sql.Timestamp;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.amazonaws.example.fileserver.repository.S3Repository;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.amazonaws.services.dynamodbv2.document.ItemUtils;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;
import com.amazonaws.services.dynamodbv2.streamsadapter.model.RecordAdapter;
import com.amazonaws.services.kinesis.clientlibrary.interfaces.v2.IRecordProcessor;
import com.amazonaws.services.kinesis.clientlibrary.lib.worker.ShutdownReason;
import com.amazonaws.services.kinesis.clientlibrary.types.InitializationInput;
import com.amazonaws.services.kinesis.clientlibrary.types.ProcessRecordsInput;
import com.amazonaws.services.kinesis.clientlibrary.types.ShutdownInput;
import com.amazonaws.services.kinesis.model.Record;

public class OutboundProcessor implements IRecordProcessor {

	private static final Log log = LogFactory.getLog(OutboundProcessor.class);
	private Integer checkpointCounter;

	private S3Repository s3Repository;

	public OutboundProcessor(S3Repository s3Repository) {
		this.s3Repository = s3Repository;
	}

	@Override
	public void initialize(InitializationInput initializationInput) {
		checkpointCounter = 0;
	}

	@Override
	public void processRecords(ProcessRecordsInput processRecordsInput) {
		List<Record> records = processRecordsInput.getRecords();
		
		StringBuilder sb = new StringBuilder();
		
		for (Record record : records) {
			if (record instanceof RecordAdapter) {
				com.amazonaws.services.dynamodbv2.model.Record streamRecord = ((RecordAdapter) record)
						.getInternalObject();

				switch (streamRecord.getEventName()) {
				case "INSERT":
					// ignoring Insert as newly created record also triggers modify
					log.info("INSERT found: " + streamRecord.getDynamodb().getNewImage());
				case "MODIFY":
					log.info("MODIFY found: " + streamRecord.getDynamodb().getNewImage());
					Map<String, AttributeValue> valueMap = streamRecord.getDynamodb().getNewImage();
					if (valueMap.containsKey("originRegion") == false) {
						log.error("Attribute originRegion is null or empty. It must be populated with a value");
						
					} else if (valueMap.get("originRegion").getS().equals("cn-north-1") == false) {
						sb.append(ItemUtils.toItem(streamRecord.getDynamodb().getNewImage()).toJSON());
					} else {
						log.info("omitting a record:" + streamRecord.toString());
					}
					break;
				case "REMOVE":
					// ignoring Remove because we do not anticipate removal in the business case. In case removal is required, implement here.
					log.info("REMOVE found: " + streamRecord.getDynamodb().getNewImage());
				}

			}
			checkpointCounter += 1;
			if (checkpointCounter % 10 == 0) {
				try {
					processRecordsInput.getCheckpointer().checkpoint();
				} catch (Exception e) {
					log.error(e);
				}
			}
		}
		
		s3Repository.writeOutbound(UUID.randomUUID().toString() + "-" + new Timestamp(System.currentTimeMillis()).toString(), sb.toString());

	}

	@Override
	public void shutdown(ShutdownInput shutdownInput) {
		if (shutdownInput.getShutdownReason() == ShutdownReason.TERMINATE) {
			try {
				shutdownInput.getCheckpointer().checkpoint();
			} catch (Exception e) {
				log.error(e);
			}
		}
	}

}
