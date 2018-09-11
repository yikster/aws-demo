package com.amazonaws.example.fileserver.syncher.marshaller;

import java.io.IOException;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.amazonaws.example.fileserver.syncher.schema.LookupData;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBTypeConverter;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser.Feature;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

@Component
public class LookupDataConverter implements DynamoDBTypeConverter<String, List<LookupData>> {

	private static final Log log = LogFactory.getLog(LookupDataConverter.class);
	
	@Autowired
	DynamoDBMapper mapper;

	@Override
	@Deprecated
	public String convert(List<LookupData> objects) {
		// Jackson object mapper
		ObjectMapper objectMapper = new ObjectMapper();
		try {
			String objectsString = objectMapper.writeValueAsString(objects);
			return objectsString;
		} catch (JsonProcessingException e) {
            log.error(e);
		}
		return null;
	}

	@Override
    public List<LookupData> unconvert(String doc) {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(Feature.ALLOW_UNQUOTED_FIELD_NAMES, true);
        try {
            List<LookupData> mappedObjects = objectMapper.readValue(doc, new TypeReference<List<LookupData>>(){});
            return mappedObjects;
        } catch (JsonParseException e) {
            log.error(e);
        } catch (JsonMappingException e) {
            log.error(e);
        } catch (IOException e) {
            log.error(e);
        }
        return null;
    }
}