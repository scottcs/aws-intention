"""REST Values API."""
import os

from .rest import RestAPI
from .db import DBClient, DEV_USER


class ValuesAPI(RestAPI):
    """Values API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['USERS_TABLE'], id_string='email', debug=self.debug)

    def _post(self):
        try:
            body = {'values': self.body}
        except KeyError:
            return self._respond(message='Body must specify "values" list.', status=400)
        response = self.db.update(DEV_USER, body)
        return self._respond(message=response.message, status=response.status)

    def _get(self):
        response = self.db.get(DEV_USER)
        try:
            values = response.response['Item']['values']
            status = response.status
        except (KeyError, TypeError):
            values = []
            status = 500
        return self._respond(None, body=values, status=status)
