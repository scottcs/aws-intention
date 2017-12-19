"""REST Values API."""
import os

from .rest import RestAPI
from .db import DBClient


class ValuesAPI(RestAPI):
    """Values API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['USERS_TABLE'], id_string='email', debug=self.debug)

    def _get(self):
        return self._respond('GET invoked - Values')
