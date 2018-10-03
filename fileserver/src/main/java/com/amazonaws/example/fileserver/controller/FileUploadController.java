package com.amazonaws.example.fileserver.controller;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

import com.amazonaws.example.fileserver.model.FileInfo;
import com.amazonaws.example.fileserver.repository.DDBRepository;
import com.amazonaws.example.fileserver.repository.S3Repository;
import com.amazonaws.example.fileserver.service.FileSystemStorageService;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.entity.mime.content.StringBody;
import org.apache.http.impl.client.HttpClientBuilder;
import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.method.annotation.MvcUriComponentsBuilder;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.amazonaws.example.fileserver.exception.StorageFileNotFoundException;
import com.amazonaws.example.fileserver.service.StorageService;

@Controller
public class FileUploadController {
    Log log = LogFactory.getLog(FileUploadController.class);

    private final StorageService storageService;


    @Autowired
    public S3Repository s3Repository;

    @Autowired
    public DDBRepository ddbRepository;

    @Autowired
    public FileUploadController() {
         this.storageService = new FileSystemStorageService();
    }

    public File createTempFile() throws Exception{
        File tempFile = File.createTempFile("tmp"+System.currentTimeMillis(), "suffix");

        BufferedWriter writer = null;
        try
        {
            writer = new BufferedWriter( new FileWriter( tempFile));
            writer.write( "ThisIsTemporaryFile");

        }
        finally
        {
            if ( writer != null)
                writer.close( );

        }

        return tempFile;

    }

    // https://docs.aws.amazon.com/ko_kr/sdk-for-java/v1/developer-guide/examples-s3-objects.html#download-object
    @GetMapping("/download")
    public ResponseEntity<Resource> download(@RequestParam("guid") String guid,
                             Model model) throws Exception {

        FileInfo fileInfo = ddbRepository.getByGuid(guid);


        Resource resource = new InputStreamResource(s3Repository.getObject(fileInfo.getBucket(), fileInfo.getObjectKey()).getObjectContent());
        String contentType = "application/octet-stream";
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + fileInfo.getFilePath() + "\"")
                .body(resource);
    }


    @GetMapping("/clienttest")
    public String clientTest(@RequestParam("bucket") String bucket,
                             @RequestParam("objectKey") String objectKey,
                             Model model) throws Exception {
        // referred from https://www.baeldung.com/httpclient-multipart-upload


        HttpPost httppost = new HttpPost("http://localhost:8080/");
        MultipartEntityBuilder builder = MultipartEntityBuilder.create();
        builder.addBinaryBody("file", createTempFile(), ContentType.DEFAULT_BINARY, "filename.ext");
        builder.addTextBody("bucket", bucket);
        builder.addTextBody("objectKey", objectKey);
        HttpEntity httpEntity = builder.build();

        httppost.setEntity(httpEntity);
        HttpResponse response = HttpClientBuilder.create().build().execute(httppost);
        log.debug(response.toString());
        return listUploadedFiles(bucket, model);





    }
    @PostMapping("/delete")
    public String deleteFile(@RequestParam("bucket") String bucket,
                             @RequestParam("objectKey") String objectKey,
                             @RequestParam("guid") String guid,
                             Model model) throws IOException {

        FileInfo fileInfo = ddbRepository.getByGuid(guid);
        try {
            storageService.delete(fileInfo.getFilePath());
        } catch(Exception e) {
            log.info("exception to delete localfile:" + e);
        }

        // TODO need to add additional key, sort key is maybe createdAt
        ddbRepository.deleteOne(guid);
        s3Repository.delete(bucket, objectKey);

        return listUploadedFiles(bucket, model );
    }
    @GetMapping("/")
    public String listUploadedFiles(@RequestParam("bucket") String bucket,
                                                Model model) throws IOException {


        model.addAttribute("files", storageService.loadAll().map(
                path -> MvcUriComponentsBuilder.fromMethodName(FileUploadController.class,
                        "serveFile", path.getFileName().toString()).build().toString())
                .collect(Collectors.toList()));
        model.addAttribute( "bucketFiles", s3Repository.objectList(bucket));
        model.addAttribute("DynamoDBFiles", ddbRepository.scan());

        return "uploadForm";
    }

    @GetMapping("/files/{filename:.+}")
    @ResponseBody
    public ResponseEntity<Resource> serveFile(@PathVariable String filename) {

        Resource file = storageService.loadAsResource(filename);
        return ResponseEntity.ok().header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename=\"" + file.getFilename() + "\"").body(file);
    }

    @PostMapping("/")
    public String handleFileUpload(@RequestParam("file") MultipartFile file,
                                   @RequestParam("bucket") String bucket,
                                   @RequestParam("objectKey") String objectKey,
                                   RedirectAttributes redirectAttributes) {

        String savedFileName = storageService.store(file);


        try {
            s3Repository.store(bucket, objectKey, file.getInputStream());
        } catch (IOException e) {
            e.printStackTrace();
            // TODO add SNS notification or add SQS or add SES failure
        }

        String newGuid = UUID.randomUUID().toString();
        ddbRepository.addNewFileRecord(new FileInfo(newGuid, bucket, objectKey, savedFileName, file.getSize()));

        redirectAttributes.addFlashAttribute("message",
                "You successfully uploaded " + file.getOriginalFilename() + "!");

        return "redirect:/?bucket=" + bucket;
    }

    @ExceptionHandler(StorageFileNotFoundException.class)
    public ResponseEntity<?> handleStorageFileNotFound(StorageFileNotFoundException exc) {
        return ResponseEntity.notFound().build();
    }

}
