package com.amazonaws.example.fileserver.syncher.marshaller;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBTypeConverter;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.ItemUtils;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser.Feature;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

@Component
public class ItemConverter implements DynamoDBTypeConverter<String, List<Item>> {
	
	private static final Log log = LogFactory.getLog(ItemConverter.class);

	@Autowired
	DynamoDBMapper mapper;

	@Override
	public String convert(List<Item> objects) {
		System.out.println(objects);
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

	@Deprecated
	@Override
    public List<Item> unconvert(String doc) {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(Feature.ALLOW_UNQUOTED_FIELD_NAMES, true);
        try {
            List<Map<String,AttributeValue>> mappedObjects = objectMapper.readValue(doc, new TypeReference<List<Map<String,AttributeValue>>>(){});
            return ItemUtils.toItemList(mappedObjects);
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