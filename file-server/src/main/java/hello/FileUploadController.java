package hello;

import java.io.File;
import java.io.IOException;
import java.util.stream.Collectors;

import com.amazonaws.example.fileserver.model.FileInfo;
import com.amazonaws.example.fileserver.repository.DDBRepository;
import com.amazonaws.example.fileserver.repository.S3Repository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.method.annotation.MvcUriComponentsBuilder;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import hello.storage.StorageFileNotFoundException;
import hello.storage.StorageService;

@Controller
public class FileUploadController {

    private final StorageService storageService;


    @Autowired
    public S3Repository s3Repository;

    @Autowired
    public DDBRepository ddbRepository;

    @Autowired
    public FileUploadController(StorageService storageService) {
        this.storageService = storageService;
    }

    @GetMapping("/")
    public String listUploadedFiles(Model model) throws IOException {

        model.addAttribute("files", storageService.loadAll().map(
                path -> MvcUriComponentsBuilder.fromMethodName(FileUploadController.class,
                        "serveFile", path.getFileName().toString()).build().toString())
                .collect(Collectors.toList()));

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

        storageService.store(file);


        // TODO
        try {
            s3Repository.store(bucket, objectKey, file.getInputStream());
        } catch (IOException e) {
            e.printStackTrace();
            // TODO add SNS notification or add SQS or add SES failure
        }

        // TODO
        ddbRepository.addNewFileRecord(new FileInfo(bucket, file.getOriginalFilename(), file.getSize()));

        redirectAttributes.addFlashAttribute("message",
                "You successfully uploaded " + file.getOriginalFilename() + "!");

        return "redirect:/";
    }

    @ExceptionHandler(StorageFileNotFoundException.class)
    public ResponseEntity<?> handleStorageFileNotFound(StorageFileNotFoundException exc) {
        return ResponseEntity.notFound().build();
    }

}
