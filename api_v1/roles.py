"""REST Roles API."""
import os

from .rest import RestAPI, ValidationException
from .db import DBClient
from utils import unique_list


class RolesAPI(RestAPI):
    """Roles API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBClient(os.environ['USERS_TABLE'], id_string='email', debug=self.debug)

    @staticmethod
    def _validate_role(role):
        if not isinstance(role, dict):
            raise ValidationException('Role is expected to be a dict')
        if 'name' not in role:
            raise ValidationException('"name" expected in body')
        if 'values' not in role:
            raise ValidationException('"values" expected in body')
        if not isinstance(role['values'], list):
            raise ValidationException('"values" must be a list.')
        try:
            if not isinstance(role['aliases'], list):
                raise ValidationException('"aliases" must be a list.')
        except KeyError:
            pass

    @staticmethod
    def _is_value_defined(value, response):
        try:
            defined_values = response.response['Item']['values']
        except (KeyError, TypeError):
            defined_values = []
        return value in [v['name'] for v in defined_values]

    def _post(self):
        try:
            self._validate_role(self.body)
        except ValidationException as exc:
            return self._respond(message=str(exc), status=400)
        response = self.db.get(self.db.current_user())
        try:
            roles = response.response['Item']['roles']
        except (KeyError, TypeError):
            roles = []
        if self.body['name'] in [r['name'] for r in roles]:
            return self._respond(message='Resource already exists', status=400)
        for value in self.body['values']:
            if not self._is_value_defined(value, response):
                return self._respond(message=f'Undefined value "{value}"', status=400)
        roles.append({
            'name': self.body['name'],
            'values': self.body['values'],
            'aliases': unique_list(self.body.get('aliases', [])),
        })
        response = self.db.update(self.db.current_user(), {'roles': roles})
        return self._respond(message=response.message, status=response.status)

    def _put(self):
        try:
            self._validate_role(self.body)
        except ValidationException as exc:
            return self._respond(message=str(exc), status=400)
        response = self.db.get(self.db.current_user())
        try:
            roles = response.response['Item']['roles']
        except (KeyError, TypeError):
            return self._respond(message='Not Found', status=404)
        if self.path_parameters['name'] not in [r['name'] for r in roles]:
            return self._respond(message='Not Found', status=404)
        for value in self.body['values']:
            if not self._is_value_defined(value, response):
                return self._respond(message=f'Undefined value "{value}"', status=400)
        for role in roles:
            if role['name'] == self.path_parameters['name']:
                role.update({
                    'name': self.body['name'],
                    'values': self.body['values'],
                    'aliases': unique_list(self.body.get('aliases', [])),
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
        message = response.message
        if 'Item updated' in message:
            message = 'Resource removed'
        return self._respond(message=message, status=response.status)

    def _get(self):
        response = self.db.get(self.db.current_user())
        try:
            roles = response.response['Item']['roles']
        except (KeyError, TypeError):
            return self._respond(message='Not Found', status=404)
        if 'name' in self.path_parameters:
            for role in roles:
                if role['name'] == self.path_parameters['name']:
                    return self._respond(None, body=role)
            return self._respond(message='Not Found', status=404)
        return self._respond(None, body=roles)
