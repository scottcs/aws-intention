"""Handler for base API route."""
from api_v1.users import UsersAPI
from api_v1.values import ValuesAPI


def users(event, context):
    """Users API handler.

    :param event: Lambda event
    :param context: Lambda context
    :return: Response dict
    """
    return UsersAPI(event, context).invoke()


def values(event, context):
    """Values API handler.

    :param event: Lambda event
    :param context: Lambda context
    :return: Response dict
    """
    return ValuesAPI(event, context).invoke()
