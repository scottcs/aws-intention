"""REST Users API."""
import os

from .rest import RestAPI
from .db import DBClient


class UsersAPI(RestAPI):
    """Users API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['USERS_TABLE'], id_string='email', debug=self.debug)

    def _post(self):
        try:
            email = self.body['email']
        except KeyError:
            return self._respond('Body must contain "email".', status=400)
        body = {}
        response = self.db.create(email, body)
        return self._respond(response.message, status=response.status)
