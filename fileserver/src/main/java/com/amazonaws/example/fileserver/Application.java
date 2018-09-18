package com.amazonaws.example.fileserver;

import com.amazonaws.example.fileserver.config.AWSConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

import org.springframework.web.SpringServletContainerInitializer;


@SpringBootApplication
@EnableConfigurationProperties(AWSConfig.StorageProperties.class)
public class Application extends SpringServletContainerInitializer {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
/*
    @Bean
    CommandLineRunner init(StorageService storageService) {
        return (args) -> {
            storageService.deleteAll();
            storageService.init();
        };
    }
*/
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(Application.class);
    }
}
