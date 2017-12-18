"""Handler for base API route."""
from lambda_api.root import RootAPI
from lambda_api.values import ValuesAPI


def root(event, context):
    """Root API handler.

    :param event: Lambda event
    :param context: Lambda context
    :return: Response dict
    """
    return RootAPI(event, context).invoke()


def values(event, context):
    """Values API handler.

    :param event: Lambda event
    :param context: Lambda context
    :return: Response dict
    """
    return ValuesAPI(event, context).invoke()
