"""REST Goals API."""
import os
import uuid

from .rest import RestAPI, ValidationException
from .db import DBClient


class GoalsAPI(RestAPI):
    """Goals API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['GOALS_TABLE'], debug=self.debug)
        self.user_db = DBClient(os.environ['USERS_TABLE'], debug=self.debug)

    def _validate_goal(self, goal, update=False):
        if not isinstance(goal, dict):
            raise ValidationException('Goal is expected to be a dict')
        if 'name' not in goal and not update:
            raise ValidationException('"name" expected in body')
        if 'role' not in goal and not update:
            raise ValidationException('"role" expected in body')
        if 'role' in goal:
            role = goal['role']
            if not self._is_role_defined(role):
                raise ValidationException(f'Undefined role "{role}"')

    def _is_role_defined(self, role):
        response = self.user_db.get(self.user_db.current_user())
        try:
            defined_roles = response.response['Item']['roles']
        except (KeyError, TypeError):
            defined_roles = []
        return role in [r['name'] for r in defined_roles]

    def _make_body(self, update=False):
        body = {
            'user': self.db.current_user(),
            'name': self.body['name'],
            'role': self.body['role'],
        }
        for key in ('notes', 'parent', 'due', 'repeat'):
            if key in self.body:
                body[key] = self.body[key]
        if update:
            for key in ('complete',):
                if key in self.body:
                    body[key] = self.body[key]
        return body

    def _post(self):
        try:
            self._validate_goal(self.body)
        except ValidationException as exc:
            return self._respond(message=str(exc), status=400)
        goal_id = str(uuid.uuid4())
        response = self.db.create(goal_id, self._make_body())
        return self._respond(response.message, status=response.status)
