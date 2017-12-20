"""REST Goals API."""
import os

from .rest import RestAPI
from .db import DBClient


class GoalsAPI(RestAPI):
    """Goals API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['GOALS_TABLE'], debug=self.debug)

    def _post(self):
        try:
            goal_id = self.body['id']
        except KeyError:
            return self._respond('Body must contain "id".', status=400)
        body = {}
        response = self.db.create(goal_id, body)
        return self._respond(response.message, status=response.status)
