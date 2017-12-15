"""REST API Root route."""
from .rest import RestAPI


class RootAPI(RestAPI):
    """Root route '/' API."""

    def _get(self):
        return self._respond('GET invoked')

    def _post(self):
        return self._respond('POST invoked')
