'''
middleware to log any failed request (error code >= 400)
'''
import json
import logging

import sqlalchemy

from potion_shop.database.logging.manager import get_logger

class LogHTTPErrors:
    def __init__(self):
        # need to getLogger AFTER it has been configured
        self.logger = get_logger()

    def _get_json(self, body):
        if not body:
            return None

        try:
            return json.loads(body)
        except json.JSONDecodeError: # pragma: no cover
        # these options exist only to catch unexpected types
        # so that logging doesn't cause additional HTTP 500 errors
        # and the user gets an informative error message
            if type(body) == bytes:
                return body.decode('utf-8')
            else:
                try:
                    return {'body_value': body}
                except:
                    return f'ERROR: Unable to parse body. type(body)={type(body)}'

    def process_response(self, req, resp, resource, req_succeeded):
        if not req_succeeded:
            req_body = self._get_json(req.context.body) if req.content_length else None
            resp_body = self._get_json(resp.body)

            self.logger.exception('Request Error', extra={
                'request_route':f'{req.method} : {req.relative_uri}',
                'request_headers':req.headers,
                'request_body':req_body,
                'response_body':resp_body,
                'response_status':resp.status
            })
