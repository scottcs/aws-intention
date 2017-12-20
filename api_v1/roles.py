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
        try:
            name = self.body['name']
        except (KeyError, TypeError):
            return self._respond(message='"name" expected in body', status=400)
        try:
            values = self.body['values']
            if not isinstance(values, list):
                return self._respond(message='"values" must be a list.', status=400)
        except (KeyError, TypeError):
            return self._respond(message='"values" expected in body', status=400)
        try:
            aliases = self.body['aliases']
            if not isinstance(aliases, list):
                return self._respond(message='"aliases" must be a list.', status=400)
        except (KeyError, TypeError):
            aliases = []
        response = self.db.get(self.db.current_user())
        try:
            roles = response.response['Item']['roles']
        except (KeyError, TypeError):
            roles = []
        if name in [r['name'] for r in roles]:
            return self._respond(message='Resource already exists', status=400)
        try:
            defined_values = response.response['Item']['values']
        except (KeyError, TypeError):
            defined_values = []
        for value in values:
            if value not in [v['name'] for v in defined_values]:
                return self._respond(message=f'Undefined value "{value}"', status=400)
        roles.append({
            'name': name,
            'values': values,
            'aliases': unique_list(aliases)
        })
        response = self.db.update(self.db.current_user(), {'roles': roles})
        return self._respond(message=response.message, status=response.status)

    def _delete(self):
        response = self.db.get(self.db.current_user())
        try:
            roles = response.response['Item']['roles']
        except (KeyError, TypeError):
            return self._respond(message='Not Found', status=404)
        if self.path_parameters['name'] not in [r['name'] for r in roles]:
            return self._respond(message='Not Found', status=404)
        new_roles = []
        for role in roles:
            if self.path_parameters['name'] != role['name']:
                new_roles.append(role)
        response = self.db.update(self.db.current_user(), {'roles': new_roles})
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
