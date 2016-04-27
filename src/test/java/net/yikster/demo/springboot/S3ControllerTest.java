package net.yikster.demo.springboot;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import static org.junit.Assert.assertNotNull;

/**
 * Created by kyoungsu on 4/27/16.
 */
@RunWith(SpringRunner.class)
@SpringBootTest
public class S3ControllerTest {
    @Autowired S3Controller s3Controller;
    @Test
    public void getS3() throws Exception {
        String time = s3Controller.getS3("httpget.py");
        System.out.println("TIme: "+ time);
        assertNotNull(time);
    }

}