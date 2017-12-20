"""REST Values API."""
import os

from .rest import RestAPI
from .db import DBClient
from utils import unique_list


class ValuesAPI(RestAPI):
    """Values API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['USERS_TABLE'], id_string='email', debug=self.debug)

    def _post(self):
        try:
            name = self.body['name']
        except (KeyError, TypeError):
            return self._respond(message='"name" expected in body', status=400)
        response = self.db.get(self.db.current_user())
        try:
            values = response.response['Item']['values']
        except (KeyError, TypeError):
            values = []
        if name in [v['name'] for v in values]:
            return self._respond(message='Resource already exists', status=400)
        values.append({'name': name})
        response = self.db.update(self.db.current_user(), {'values': values})
        return self._respond(message=response.message, status=response.status)

    def _delete(self):
        response = self.db.get(self.db.current_user())
        try:
            values = response.response['Item']['values']
        except (KeyError, TypeError):
            return self._respond(message='Not Found', status=404)
        if self.path_parameters['name'] not in [v['name'] for v in values]:
            return self._respond(message='Not Found', status=404)
        new_values = []
        for value in values:
            if self.path_parameters['name'] != value['name']:
                new_values.append(value)
        response = self.db.update(self.db.current_user(), {'values': new_values})
        message = response.message
        if 'Item updated' in message:
            message = 'Resource removed'
        return self._respond(message=message, status=response.status)

    def _get(self):
        response = self.db.get(self.db.current_user())
        try:
            values = response.response['Item']['values']
            status = response.status
            message = None
        except (KeyError, TypeError):
            values = []
            status = 404
            message = 'Not Found'
        return self._respond(message, body=values, status=status)
