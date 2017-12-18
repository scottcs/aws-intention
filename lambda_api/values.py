"""REST Values API."""
from .rest import RestAPI


class ValuesAPI(RestAPI):
    """Values API."""

    def _get(self):
        return self._respond('GET invoked - Values')
