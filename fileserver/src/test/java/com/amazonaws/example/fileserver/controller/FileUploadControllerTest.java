package com.amazonaws.example.fileserver.controller;

import com.amazonaws.example.fileserver.Application;
import com.amazonaws.example.fileserver.config.AWSConfig;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MockMvcBuilder;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import static org.junit.Assert.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;


@RunWith(SpringRunner.class)
@WebMvcTest(FileUploadController.class)
//@SpringBootTest
//@AutoConfigureMockMvc
public class FileUploadControllerTest {

    @Autowired
    MockMvc mockMvc;

//    @Autowired
//    TestRestTemplate testRestTemplate;

    @MockBean
    FileUploadController fileUploadController;

    @Before
    public void setup(){
//        MockMvcBuilders.webAppContextSetup()
//        this.mockMvc = MockMvcBuilders.standaloneSetup(new FileUploadController()).build();
    }
    @Test
    public void clientTest() throws Exception {
        assertNotNull(fileUploadController);
        String result = fileUploadController.clientTest("ks-test-icn", "test1", null);
        System.out.println("result" +
                ":" + result);
//        assertNotNull(testRestTemplate);
        assertNotNull(mockMvc);
        mockMvc.perform(get("/clienttest").param("bucket", "ks-test-icn").param("objectKey", "test1"))
                .andDo(print())
                .andExpect(status().isOk());
    }
}