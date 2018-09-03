/*
 * permissions and limitations under the License.
 */

/* Imports */
var AWS = require('aws-sdk');

/* Globals */
var esDomain = {
    endpoint: 'vpc-guardduty-zzzzzzzzzzzzzzzzzzzzz.ap-northeast-2.es.amazonaws.com',
    region: 'ap-northeast-2',
    index: 'guardduty',
    doctype: '_doc'
};
var processed = 0;
var records = 0;

var endpoint =  new AWS.Endpoint(esDomain.endpoint);

function postDocumentToES(doc, context) {
    var creds = new AWS.EnvironmentCredentials('AWS');



/*
 * Add the given document to the ES domain.
 * If all records are successfully added, indicate success to lambda
 * (using the "context" parameter).
 */
    var req = new AWS.HttpRequest(endpoint);
    
    req.method = 'POST';
    req.path = "/" + esDomain.index + '/' + esDomain.doctype +"/";
    req.region = esDomain.region;
    req.body = doc;
    req.headers['presigned-expires'] = false;
    req.headers['Host'] = endpoint.host;
    req.headers['Content-type'] = "application/json";

    // Sign the request (Sigv4)
    var signer = new AWS.Signers.V4(req, 'es');
    signer.addAuthorization(creds, new Date());

    // Post document to ES
    var send = new AWS.NodeHttpClient();
    send.handleRequest(req, null, function(httpResp) {
        var body = '';
        httpResp.on('data', function (chunk) {
            body += chunk;
        });
        httpResp.on('end', function (chunk) {
            processed ++;
            console.log(" " + processed + " / " + records + " processed !");
    
            if( processed >= records)
                context.succeed();
            
        });
    }, function(err) {
        console.log('Error: ' + err);
        context.fail();
    });
}

function validRecord(event, context) {
    // console.log(event);
    // console.log(event);
    if(undefined != event.detail) {
        event = event.detail;
    } 
    if(undefined != event.resource.insetanceDetails) {
        event.resource.instanceDetails.launchDateTime = event.resource.instanceDetails.launchTime;
        delete event.resource.instanceDetails.launchTime;
    }
    
    if(undefined != event.service.action.actionType) {
        console.log("Processing..." + event.service.action.actionType);
        if("PORT_PROBE" == event.service.action.actionType) {
            var detail = event.service.action.portProbeAction.portProbeDetails[0]
            event.localPort = detail.localPortDetails.port;
            event.localPortName = detail.localPortDetails.portName;
            event.remote = detail.remoteIpDetails;
            event.location = [detail.remoteIpDetails.geoLocation.lon, detail.remoteIpDetails.geoLocation.lat];
            console.log("PORT_PROBE:" + event.location);
        } else if("NETWORK_CONNECTION" == event.service.action.actionType) {
            var detail = event.service.action.networkConnectionAction
            
            // event.localPort = detail.localPortDetails.port;
            // event.localPortName = detail.localPortDetails.portName;
            event.remote = detail.remoteIpDetails;
            event.location = [detail.remoteIpDetails.geoLocation.lon, detail.remoteIpDetails.geoLocation.lat];
            console.log("NET_REMOTE:" + event.location);
        } else {
            console.log("Undefined process for :" + event.service.action.actionType);
        }
        postDocumentToES(JSON.stringify(event), context);
        
    }
}

/* Lambda "main": Execution starts here */
exports.handler = function(event, context) {
    if(undefined != event.Records && event.Records.length > 0) {
        records = event.Records.length;
        event.Records.forEach(function(record){
            validRecord(record, context)
        });
    } else {
        records = 1;
        validRecord(event, context);
        
    }
    console.log(" " + processed + " / " + records + " processed !");
}
