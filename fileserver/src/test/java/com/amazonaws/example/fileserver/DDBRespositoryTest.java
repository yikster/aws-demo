package com.amazonaws.example.fileserver;

import com.amazonaws.example.fileserver.model.FileInfo;
import com.amazonaws.example.fileserver.repository.DDBRepository;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

@RunWith(SpringRunner.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)

public class DDBRespositoryTest {
    @Autowired
    DDBRepository ddbRepository;

    @Test
    public void test() {
        ddbRepository.addNewFileRecord(new FileInfo("ks-test-icn", "test.key", 10));
    }
}
