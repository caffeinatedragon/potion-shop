'''
Reads the body of all requests. Stores body into req.context.body
Necessary for logging, so that request body can be duplicated to log.
If it was just processed in the request, wouldn't be able to read again
for the log because the stream.read operation had already run once.
'''
class StreamHandler:
    def process_request(self, req, resp):
        if req.content_length:
            req.context.body = req.stream.read(req.content_length)
