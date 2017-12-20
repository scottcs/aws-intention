"""aws_intention - rest_api"""
import json
import logging

from .decimal_encoder import DecimalEncoder


HTTP_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'COPY',
    'HEAD',
    'OPTIONS',
    'LINK',
    'UNLINK',
    'PURGE',
    'LOCK',
    'UNLOCK',
    'PROPFIND',
    'VIEW',
)


class ValidationException(Exception):
    """API Validation failure."""


class RestAPI:
    """HTTP REST API handler.

    Subclass this class and implement _method() methods for each HTTP METHOD you want to support.

    `_options()` is already provided for you.

    For example, to support GET and POST, implement `_get()` and `_post()`, typically
    by returning `self._respond()`.
    """

    def __init__(self, event, context):
        """Entry point from Lambda invocation.

        :param event: Lambda event
        :param context: Lambda context
        """
        self._event = event
        self._context = context
        self._body = {}
        self.log = logging.getLogger('RestAPI')
        if self.debug:
            self.log.setLevel(logging.DEBUG)

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
            except (KeyError, TypeError):
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
        context_vars = vars(self._context)
        del context_vars['identity']
        return {
            'input_event': self._event,
            'input_context': context_vars,
            'method': self.method,
            'route': self.route,
            'stage': self.stage,
            'body': self.body,
            'path_parameters': self.path_parameters,
            'query_parameters': self.query_parameters,
            'body_is_base64': self.body_is_base64,
        }

    def _respond(self, message, body=None, headers=None, status=200):
        headers = headers or {}
        body = body or {}
        if message:
            body['message'] = message
        if self.debug:
            body = {
                'response_body': body,
                'debug': self._debugging_response_data(),
            }
        return {
            'statusCode': status,
            'body': json.dumps(body, cls=DecimalEncoder),
            'headers': headers,
        }

    def _options(self):
        self.log.debug('OPTIONS invoked')
        options = []
        for method in HTTP_METHODS:
            if hasattr(self, f'_{method.lower()}'):
                options.append(method)
        headers = {}
        if options:
            opt_str = ', '.join(options)
            headers = {
                'Allow': opt_str,
            }
        else:
            opt_str = 'None'
        return self._respond(f'OPTIONS: {opt_str}', headers=headers)

    def invoke(self):
        """Parse the api_v1 event and invoke the correct method.

        :return: HTTP Response
        """
        method = getattr(self, f'_{self.method.lower()}', None)
        if method:
            return method()
        return self._respond(f'{self.method} is not implemented', status=501)
