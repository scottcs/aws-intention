"""REST Users API."""
from .rest import RestAPI


class UsersAPI(RestAPI):
    """Users API."""

    def _post(self):
        return self._respond('POST invoked - Users')
