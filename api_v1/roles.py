"""REST Roles API."""
import os

from .rest import RestAPI
from .db import DBClient
from utils import unique_list


class RolesAPI(RestAPI):
    """Roles API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['USERS_TABLE'], id_string='email', debug=self.debug)

    def _post(self):
        if not isinstance(self.body, list):
            return self._respond(message='Body must be a list.', status=400)
        response = self.db.update(self.db.current_user(), {'roles': unique_list(self.body)})
        return self._respond(message=response.message, status=response.status)

    def _get(self):
        response = self.db.get(self.db.current_user())
        try:
            roles = response.response['Item']['roles']
            status = response.status
            message = None
        except (KeyError, TypeError):
            roles = []
            status = 404
            message = 'Not Found'
        return self._respond(message, body=roles, status=status)
