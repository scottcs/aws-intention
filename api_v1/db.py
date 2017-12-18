"""DynamoDB Interface class."""
from collections import namedtuple
import logging
import os
import time

import boto3
from botocore.exceptions import ClientError

Response = namedtuple('Response', ['response', 'message', 'status'])


def _timestamp():
    """Get a timestamp of the current time."""
    return int(time.time() * 1000)


class DBClient:
    """DynamoDB client class."""

    def __init__(self, table_name=None, id_string=None, debug=False):
        self.table_name = table_name or os.environ['DYNAMODB_TABLE']
        self.id_string = id_string or 'id'
        self.table = boto3.resource('dynamodb').Table(self.table_name)
        self.log = logging.getLogger('RestAPI')
        if debug:
            self.log.setLevel(logging.DEBUG)

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
        self.log.debug('{}: PutItem: {}'.format(self.table_name, data))
        try:
            response = self.table.put_item(
                Item=data, ConditionExpression='attribute_not_exists({})'.format(self.id_string))
            return Response(response, 'Created: {}'.format(item_id), 201)
        except ClientError as exc:
            self.log.error('Client error: {}'.format(exc), exc_info=True)
            if 'ConditionalCheckFailedException' in str(exc):
                message = 'Resource already exists.'
            else:
                message = str(exc)
            try:
                return Response(None, message, int(exc.response['ResponseMetadata']['HTTPStatusCode']))
            except KeyError:
                return Response(None, str(exc), 500)

    def delete(self, item_id):
        """Delete a row from the table.

        :param item_id: Id of the item to delete.
        :return: Response
        """
        self.log.debug('{}: DeleteItem: {}'.format(self.table_name, item_id))
        response = self.table.delete_item(
            Key={
                self.id_string: item_id,
            }
        )
        return Response(response, 'Deleted: {}'.format(item_id), 200)

    def get(self, item_id):
        """Get a single item from the table.

        :param item_id: Id of the item
        :return: Response
        """
        self.log.debug('{}: GetItem: {}'.format(self.table_name, item_id))
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
        self.log.debug('{}: Scan'.format(self.table_name))
        response = self.table.scan()
        return Response(response, None, 200)

    def update(self, item_id, data):
        """Update an item in the table.

        :param item_id: Unique id for the table row
        :param data: Item data for the row
        :return: Response
        """
        attr_values = {}
        updates = []
        for k, v in data.items():
            attr_values[':{}'.format(k)] = v
            updates.append('{0} = :{0}'.format(k))
        attr_values[':updatedAt'] = _timestamp()
        update_expr = 'SET {}'.format(', '.join(updates))

        self.log.debug('{}: UpdateItem: {}  v: {}  e: {}'.format(
            self.table_name, item_id, attr_values, update_expr))
        response = self.table.update_item(
            Key={
                self.id_string: item_id,
            },
            ExpressionAttributeValues=attr_values,
            UpdateExpression=update_expr,
            ReturnValues='ALL_NEW',
        )
        return Response(response, 'Item updated: {}'.format(item_id), 200)
