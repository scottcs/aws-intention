"""Handler for base API route."""
from lambda_api.root import RootAPI


def handler(event, context):
    """Base API handler.

    :param event: Lambda event
    :param context: Lambda context
    :return: Response dict
    """
    return RootAPI(event, context).invoke()
