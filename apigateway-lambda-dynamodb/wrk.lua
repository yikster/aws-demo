wrk.method = "POST"
wrk.body = "{\"todo_id\": \"1002\", \"active\": true, \"description\": \"What TODO next?\"}"
wrk.headers["Accept-Encoding"] = "gzip"
wrk.headers["Content-Type"] = "application/json"

local counter = 1
local threads = {}

function setup(thread)
   thread:set("id", counter)
   table.insert(threads, thread)
   counter = counter + 1
end

function init(args)
   requests  = 0
   responses = 0
   successCounter = 0;
   failCounter = 0;

   local msg = "thread %d created"
   print(msg:format(id))
end

function request()
   requests = requests + 1
   return wrk.request()
end

function response(status, headers, body)
   responses = responses + 1
   if status == 200 then
      successCounter = successCounter + 1 
   else
      failCounter = failCounter + 1
   end
end

function done(summary, latency, requests)
   for index, thread in ipairs(threads) do
      local id        = thread:get("id")
      local requests  = thread:get("requests")
      local responses = thread:get("responses")
      local successCounter = thread:get("successCounter")
      local failCounter = thread:get("failCounter")
      local msg = "thread %d made %d requests and got %d responses, Status-200 : %d, Status-Not-200: %d"
      print(msg:format(id, requests, responses, successCounter, failCounter))
   end
end
