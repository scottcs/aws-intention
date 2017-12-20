"""Handler for base API route."""
from api_v1.users import UsersAPI
from api_v1.values import ValuesAPI
from api_v1.roles import RolesAPI


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


def roles(event, context):
    """Roles API handler.

    :param event: Lambda event
    :param context: Lambda context
    :return: Response dict
    """
    return RolesAPI(event, context).invoke()
