"""REST Values API."""
import os

from .rest import RestAPI
from .db import DBClient, DEV_USER
from utils import unique_list


class ValuesAPI(RestAPI):
    """Values API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['USERS_TABLE'], id_string='email', debug=self.debug)

    def _post(self):
        if not isinstance(self.body, list):
            return self._respond(message='Body must be a list.', status=400)
        response = self.db.update(DEV_USER, {'values': unique_list(self.body)})
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
