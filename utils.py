# -*- coding: utf-8 -*-
"""Module containing several utility helper functions."""
from calendar import monthrange
from datetime import datetime

from prettytable import PrettyTable

import config as cfg


def build_output_table(dictionary, is_int_expected=False):
    """
    Helper function to build the table of information.

    :param dictionary: dict
        Dict containing either the updated apps or monthly count information.
    :param is_int_expected: boolean
        Flag to indicate how to interpret None value from dictionary.
    """
    if is_int_expected:
        expected_type = 0
    else:
        expected_type = None
    table_obj = get_table_header()
    for app in dictionary:
        row = [app]
        play_store_value = dictionary[app].get('play_store', expected_type)
        if play_store_value:
            row.append('{val}'.format(val=play_store_value))
        else:
            row.append('No updates')
        for country_code in cfg.APP_STORE_COUNTRY_CODES:
            app_store_value = dictionary[app].get('app_store_' + country_code, expected_type)
            if app_store_value:
                row.append('{val}'.format(val=app_store_value))
            else:
                row.append('No updates')
        table_obj.add_row(row)
    return table_obj


def get_table_header():
    """Helper function to construct the table header."""
    header_items = ['Application', 'Google PlayStore']
    for country_code in cfg.APP_STORE_COUNTRY_CODES:
        header_items.append('Apple iTunes - ' + country_code.upper())

    return PrettyTable(header_items)


def datetime_json_handler(obj):
    """
    Custom handler for serializing datetime objects.

    The datetime objects throw a 'not JSON serializable exception'.
    This is a custom handler for datetime objects.
    :param obj: Object to check
    :return: String
    """
    if isinstance(obj, datetime):
        return obj.__str__()


def is_last_day_of_month():
    """Helper function to check whether today is last of the month."""
    today = datetime.now()
    day = today.day
    month = today.month
    year = today.year
    return day == monthrange(year, month)[1]
