"""aws_intention - rest_api"""
import json


class RestAPI:
    """HTTP REST API handler"""

    def __init__(self, event, context):
        """Entry point from Lambda invocation.

        :param event: Lambda event
        :param context: Lambda context
        """
        self._event = event
        self._context = context
        self._body = {}

    @property
    def debug(self):
        """Property is_debugging"""
        return bool(self.query_parameters.get('debug', False))

    @property
    def body_is_base64(self):
        """Property body_is_base64"""
        return self._event.get('isBase64Encoded', False)

    @property
    def path_parameters(self):
        """Property path_parameters"""
        return self._event.get('pathParameters', {}) or {}

    @property
    def query_parameters(self):
        """Property query_parameters"""
        return self._event.get('queryStringParameters', {}) or {}

    @property
    def body(self):
        """Property body"""
        if not self._body:
            try:
                self._body = json.loads(self._event['body'])
            except (KeyError, ValueError):
                pass
        return self._body

    @property
    def method(self):
        """Property method"""
        return self._event['httpMethod']

    @property
    def route(self):
        """Property route"""
        return self._event['path']

    @property
    def stage(self):
        """Property stage"""
        return self._event['requestContext']['stage']

    def _debugging_response_data(self):
        return {
            'event': self._event,
            'context': self._context,
            'method': self.method,
            'route': self.route,
            'stage': self.stage,
            'body': self.body,
            'path_parameters': self.path_parameters,
            'query_parameters': self.query_parameters,
            'body_is_base64': self.body_is_base64,
        }

    def _get(self):
        body = {
            'message': 'GET invoked',
        }
        if self.debug:
            body.update(self._debugging_response_data())
        response = {
            'statusCode': 200,
            'body': json.dumps(body)
        }
        return response

    def invoke(self):
        """Parse the lambda_api event and invoke the correct method.

        :return: HTTP Response
        """
        return getattr(self, {
            'GET': '_get',
            'POST': '_post',
            'PUT': '_put',
            'DELETE': '_delete',
        }[self.method])()
