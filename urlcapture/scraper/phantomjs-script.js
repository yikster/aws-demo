var system = require('system');
var env = system.env;
var page = require('webpage').create();
var fs = require('fs');

page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36';
page.settings.resourceTimeout = 10000;
page.viewportSize = {
  width: 800
//, height: 768
};

var error = '';

page.onResourceError = function(resourceError) {
  error = resourceError.errorString;
};

page.open(env.URL, function(status) {
  if (status == 'success') {
    function checkReadyState() {
      var readyState = page.evaluate(function() {
        return document.readyState;
      });
      if (readyState == 'complete') {
        var data = page.renderBase64("PNG");
               
 
        var result = page.evaluate(function() {
          return document.title;
//documentElement.outerHTML;
        });

        system.stdout.write(data);
        phantom.exit(0);
      }
      else {
        setTimeout(checkReadyState, 50);
      }
    }
    checkReadyState();
  }
  else {
    system.stderr.write(error);
    phantom.exit(1);
  }
});
