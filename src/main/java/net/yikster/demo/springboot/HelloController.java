package hello;



import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.*;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;

@RestController
public class HelloController {
    
    @RequestMapping("/")
    public String index() {
        return "Greetings from Spring Boot!";
    }

    @RequestMapping("/getDetails/{keyword}")
    public String getDetails(@PathVariable(value = "keyword") String keyword) {
        return  getContent(keyword);
    }

    public String getContent(String keyword) {
        DefaultHttpClient
                httpclient = new DefaultHttpClient();
        try {
            HttpGet getRequest = new HttpGet("https://en.wikipedia.org/wiki/" + keyword);
            HttpResponse httpResponse = httpclient.execute(getRequest);
            HttpEntity entity = httpResponse.getEntity();
            
			if (entity != null) {
                return EntityUtils.toString(entity);
            } 
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            httpclient.getConnectionManager().shutdown();
        }
        return "";
    }
}