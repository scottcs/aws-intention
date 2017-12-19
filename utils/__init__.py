"""Utility functions."""
from collections import OrderedDict


def unique_list(messy_list):
    """Return a list with items in order but duplicates removed.

    :param messy_list: original list
    :return: unique list
    """
    return list(OrderedDict.fromkeys(messy_list))
