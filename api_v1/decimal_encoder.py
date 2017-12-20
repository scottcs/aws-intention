"""This is a workaround for: http://bugs.python.org/issue16535"""
import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    """Support encoding decimal.Decimal objects in JSON."""
    def default(self, o, **kwargs):
        """Default encoder."""
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o, **kwargs)
