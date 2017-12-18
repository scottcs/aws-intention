"""REST Users API."""
from .rest import RestAPI
from .db import DBClient


class UsersAPI(RestAPI):
    """Users API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(id_string='email', debug=self.debug)

    def _post(self):
        email = self.body['email']
        response = self.db.create(email, self.body)
        return self._respond(response.message, status=response.status)
