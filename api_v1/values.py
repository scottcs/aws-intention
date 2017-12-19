"""REST Values API."""
import os

from .rest import RestAPI
from .db import DBClient, DEV_USER
from ..utils import unique_list


class ValuesAPI(RestAPI):
    """Values API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['USERS_TABLE'], id_string='email', debug=self.debug)

    def _post(self):
        response = self.db.get(DEV_USER)
        try:
            if response.response['Item']['values']:
                return self._respond(message='Resource already exists.', status=400)
        except (KeyError, TypeError):
            pass
        if not isinstance(self.body, list):
            return self._respond(message='Body must be a list.', status=400)
        response = self.db.update(DEV_USER, {'values': unique_list(self.body)})
        return self._respond(message=response.message, status=response.status)

    def _put(self):
        response = self.db.get(DEV_USER)
        try:
            values = response.response['Item']['values']
        except (KeyError, TypeError):
            return self._respond(message='Not Found', status=404)
        if not isinstance(self.body, list):
            return self._respond(message='Body must be a list.', status=400)
        values.extend(self.body)
        values = unique_list(values)
        response = self.db.update(DEV_USER, {'values': values})
        return self._respond(message=response.message, status=response.status)

    def _get(self):
        response = self.db.get(DEV_USER)
        try:
            values = response.response['Item']['values']
            status = response.status
            message = None
        except (KeyError, TypeError):
            values = []
            status = 404
            message = 'Not Found'
        return self._respond(message, body=values, status=status)
