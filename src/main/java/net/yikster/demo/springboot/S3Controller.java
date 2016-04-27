package net.yikster.demo.springboot;


import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3Client;
import com.amazonaws.services.s3.model.AmazonS3Exception;
import com.amazonaws.services.s3.model.GetObjectMetadataRequest;
import com.amazonaws.services.s3.model.ObjectMetadata;
import org.apache.log4j.Logger;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class S3Controller {

    Logger logger = Logger.getLogger(S3Controller.class);

    @RequestMapping("/getS3")
    public String getS3(@RequestParam("bucket") String bucket, @RequestParam("fileName") String fileName) {
        String time ="";
        ProfileCredentialsProvider profileCredentialsProvider = new ProfileCredentialsProvider("s3-readonly");
        logger.debug("AWS -KEY:" + profileCredentialsProvider.getCredentials().getAWSAccessKeyId());
        AmazonS3Client awsS3Client = new AmazonS3Client(profileCredentialsProvider);
        awsS3Client.setRegion(Region.getRegion(Regions.AP_NORTHEAST_2));
        try {
            GetObjectMetadataRequest req = new GetObjectMetadataRequest(bucket, fileName);
            ObjectMetadata objectMetadata = awsS3Client.getObjectMetadata(req);
            time = "objectMeta.lastModified:" + objectMetadata.getLastModified().getTime();

        }
        catch (AmazonS3Exception e) {
            time = "fileName:" + fileName + "<br />" +      e.getErrorCode() + "<br />" + e.toString();
            logger.error(time);
            logger.error(e);
        } catch (Exception e) {
            logger.error(e);
        } finally {

        }
        logger.debug("Time:" + time);
        return time;
    }
}

