"""DynamoDB Interface class."""
from collections import namedtuple
import logging
import time

import boto3
from botocore.exceptions import ClientError

Response = namedtuple('Response', ['response', 'message', 'status'])
DEV_USER = 'scottcs+intention1@gmail.com'


def _timestamp():
    """Get a timestamp of the current time."""
    return int(time.time() * 1000)


class DBClient:
    """DynamoDB client class."""

    def __init__(self, table_name, id_string=None, debug=False):
        self.table_name = table_name
        self.id_string = id_string or 'id'
        self.table = boto3.resource('dynamodb').Table(self.table_name)
        self.log = logging.getLogger('RestAPI')
        self._user = DEV_USER
        if debug:
            self.log.setLevel(logging.DEBUG)

    def current_user(self):
        """Get the current user.

        :return: The current user
        """
        return self._user

    def create(self, item_id, data):
        """Create an entry in the table.

        :param item_id: Unique id for the table row
        :param data: Item data for the row
        :return: Response
        """
        timestamp = _timestamp()
        data.update({
            self.id_string: item_id,
            'createdAt': timestamp,
            'updatedAt': timestamp,
        })
        self.log.debug(f'{self.table_name}: PutItem: {data}')
        try:
            response = self.table.put_item(
                Item=data, ConditionExpression=f'attribute_not_exists({self.id_string})')
            return Response(response, f'Created: {item_id}', 201)
        except ClientError as exc:
            self.log.error(f'Client error: {exc}', exc_info=True)
            if 'ConditionalCheckFailedException' in str(exc):
                message = 'Resource already exists.'
            else:
                message = str(exc)
            try:
                return Response(
                    None, message, int(exc.response['ResponseMetadata']['HTTPStatusCode']))
            except (KeyError, AttributeError):
                return Response(None, str(exc), 500)

    def delete(self, item_id):
        """Delete a row from the table.

        :param item_id: Id of the item to delete.
        :return: Response
        """
        self.log.debug(f'{self.table_name}: DeleteItem: {item_id}')
        response = self.table.delete_item(
            Key={
                self.id_string: item_id,
            }
        )
        return Response(response, f'Deleted: {item_id}', 200)

    def get(self, item_id):
        """Get a single item from the table.

        :param item_id: Id of the item
        :return: Response
        """
        self.log.debug(f'{self.table_name}: GetItem: {item_id}')
        response = self.table.get_item(
            Key={
                self.id_string: item_id,
            }
        )
        return Response(response, None, 200)

    def get_all(self):
        """Get all items from the table.

        :return: Response
        """
        self.log.debug(f'{self.table_name}: Scan')
        response = self.table.scan()
        return Response(response, None, 200)

    def update(self, item_id, data):
        """Update an item in the table.

        :param item_id: Unique id for the table row
        :param data: Item data for the row
        :return: Response
        """
        attr_names = {}
        attr_values = {}
        updates = []
        data['updatedAt'] = _timestamp()
        for k, v in data.items():
            attr_names[f'#{k}'] = k
            attr_values[f':{k}'] = v
            updates.append(f'#{k} = :{k}')
        update_expr = f'SET {", ".join(updates)}'

        self.log.debug(f'{self.table_name}: UpdateItem: {item_id}  '
                       f'n: {attr_names}  v: {attr_values}  e: {update_expr}')
        response = self.table.update_item(
            Key={
                self.id_string: item_id,
            },
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
            UpdateExpression=update_expr,
            ReturnValues='ALL_NEW',
        )
        return Response(response, f'Item updated: {item_id}', 200)
