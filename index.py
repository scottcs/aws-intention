"""Handler for base API route."""
from lambda_api.rest import RestAPI


def handler(event, context):
    """Base API handler.

    :param event: Lambda event
    :param context: Lambda context
    :return: Response dict
    """
    return RestAPI(event, context).invoke()
