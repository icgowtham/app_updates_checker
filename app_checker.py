"""
Module to check updates for certain apps.

This application tries to retrieve the information from both Google Play Store and Apple iTunes to check
for app updates.

Sometimes the page content which we retrieve from iTunes appear in a non-standard encoding which cannot be parsed.
Whenever errors are encountered, we log the error and continue so that processing of other apps are not affected.

We maintain a JSON file to store the latest results and retrieve the existing results for comparison.
"""

import argparse
import json
import os
import re

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from play_scraper import details

import config as cfg
from logger import get_logger

__author__ = 'Ishwarachandra Gowtham'
__version__ = '1.0'
__email__ = 'ic.gowtham@gmail.com'

from utils import datetime_json_handler, is_last_day_of_month, build_output_table

APP_DATA_MAP = {}
UPDATED_APPS_MAP = {}
MONTHLY_COUNT_TRACKER = {}
LOGGER = get_logger()
FAILURES = []


def check_for_updates(app):
    """
    Function to check the last updated date for a given application.

    :param app:
    :return: None
    """
    if app not in APP_DATA_MAP:
        APP_DATA_MAP.setdefault(app, {})
    play_store_id = cfg.APPS_TO_ID_MAP[app].get('play_store', None)
    if play_store_id:
        check_play_store(app, play_store_id)
    app_store_id = cfg.APPS_TO_ID_MAP[app].get('app_store', None)
    if app_store_id:
        for country_code in cfg.APP_STORE_COUNTRY_CODES:
            check_app_store(app, country_code, app_store_id)


def check_app_store(app, country_code, app_store_id):
    """
    Check iTunes for updates.

    :param app: str
        Application name.
    :param country_code: str
        Country code for iTunes.
    :param app_store_id: str
        Application identifier.
    :return: None
    """
    app_store_url = cfg.BASE_APP_STORE_URL.format(cc=country_code, id=app_store_id)
    app_store_page_content = get_webpage_contents(url=app_store_url)
    if app_store_page_content:
        as_soup = BeautifulSoup(app_store_page_content, 'html5lib')
        time_tag = as_soup.find('time')
        if not time_tag:
            LOGGER.error('App=%s - %s - Could not find the field containing the updated date!',
                         app, app_store_url)
            FAILURES.append('App={app} - {url} - Could not find the field containing the updated date.'.format(
                app=app, url=app_store_url))
            return
        last_updated = time_tag.contents
        if last_updated:
            current_value = None
            try:
                current_value = last_updated[0].encode('utf-8').decode('utf-8')
                # Sometimes, the date value contains encoded characters which are difficult to compare.
                # We are removing them to have a clean string.
                current_value = re.sub(r'[^\x00-\x7f]', r' ', current_value)
                date_val = parse(current_value)
                current_value = '{dd}/{mm}/{yyyy}'.format(dd=str(date_val.day),
                                                          mm=str(date_val.month),
                                                          yyyy=str(date_val.year))
            except Exception as exp:
                # We get some non-standard encoded values from App Store sometimes which cause parsing errors.
                # Normally when the application is re-run, the error goes away most of the time.
                LOGGER.error('App=%s - %s - Exception while trying to parse or decode the value: %s',
                             app, app_store_url, str(exp))
                FAILURES.append(
                    'App={app} - {url} - Exception while trying to parse or decode the value: {exp}'.format(
                        app=app, url=app_store_url, exp=str(exp))
                )
                return
            LOGGER.info('APP STORE-{cc}: {app} - {upd}'.format(
                cc=country_code.upper(), app=app, upd=current_value))
            old_value = APP_DATA_MAP[app].get('app_store_' + country_code, None)
            if not old_value or old_value != current_value:
                update_data_store(app, 'app_store_' + country_code, current_value)
        else:
            LOGGER.error('App=%s - %s - Could not retrieve date value!',
                         app, app_store_url)
            FAILURES.append('App={app} - {url} - Could not retrieve the date value!'.format(
                app=app, url=app_store_url))
    else:
        LOGGER.error('App=%s - %s - did not fetch any results.', app, app_store_url)
        FAILURES.append('App={app} - {url} - did not fetch any results.'.format(
            app=app, url=app_store_url))


def check_play_store(app, play_store_id):
    """
    Check Google PlayStore for updates.

    :param app: str
        Name of the application.
    :param play_store_id: str
        Application identifier.
    :return: None
    """
    # We are not reinventing the wheel for Play Store since there is already
    # a module which does the stuff which we want.
    current_value = details(play_store_id).get('updated', None)
    if current_value:
        date_val = parse(current_value)
        current_value = '{dd}/{mm}/{yyyy}'.format(dd=str(date_val.day),
                                                  mm=str(date_val.month),
                                                  yyyy=str(date_val.year))
        LOGGER.info('PLAY STORE: {app} - {upd}'.format(app=app, upd=current_value))
        old_value = APP_DATA_MAP[app].get('play_store', None)
        if not old_value or old_value != current_value:
            update_data_store(app, 'play_store', current_value)
    else:
        play_store_url = cfg.BASE_PLAY_STORE_URL.format(id=play_store_id)
        LOGGER.error('App=%s - %s - did not fetch any results.', app, play_store_url)
        FAILURES.append('App={app} - {url} - did not fetch any results.'.format(
            app=app, url=play_store_url))


def update_data_store(app, key, value):
    """
    Helper function to update the data store.

    :param app: str
        Name of the app.
    :param key: str
        Key used in the data store, like 'play_store', 'app_store_in', etc.
    :param value: str
        Updated value.
    :return: None
    """
    UPDATED_APPS_MAP.setdefault(app, {})
    UPDATED_APPS_MAP[app][key] = value
    APP_DATA_MAP[app][key] = value
    if app not in MONTHLY_COUNT_TRACKER:
        MONTHLY_COUNT_TRACKER.setdefault(app, {})
    update_count = MONTHLY_COUNT_TRACKER[app].get(key, 0)
    update_count += 1
    MONTHLY_COUNT_TRACKER[app][key] = update_count


def get_webpage_contents(url):
    """
    Function to get the contents of a web page.

    :param url: str
        The URL for the web page.
    :return: object
        Content of the web page or None.
    """
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        return response.content
    return None


def print_table():
    """
    Function to print the output table.

    :return: None
    """
    if UPDATED_APPS_MAP:
        print('The below apps have updates.')
        print(build_output_table(UPDATED_APPS_MAP))
    else:
        print('No App Updates Found.')
    if MONTHLY_COUNT_TRACKER:
        print('Summary of number of app updates for this month:')
        print(build_output_table(MONTHLY_COUNT_TRACKER, True))
    if FAILURES:
        print('The following errors were encountered while trying to fetch the details:')
        for item in FAILURES:
            print(item)


def main(app=None):
    """
    Application entry-point.

    :param app: str
        Name of the application to check.
    :return: None
    """
    global APP_DATA_MAP, MONTHLY_COUNT_TRACKER

    if os.path.exists(cfg.DATA_STORE):
        with open(cfg.DATA_STORE, 'r') as fh:
            APP_DATA_MAP = json.load(fh)

    if os.path.exists(cfg.COUNT_TRACKER):
        with open(cfg.COUNT_TRACKER, 'r') as fh:
            MONTHLY_COUNT_TRACKER = json.load(fh)

    if app:
        applications_to_check = [app]
    else:
        applications_to_check = list(cfg.APPS_TO_ID_MAP.keys())

    for app in applications_to_check:
        check_for_updates(app)

    print_table()

    if UPDATED_APPS_MAP:
        with open(cfg.DATA_STORE, 'w') as fh:
            json.dump(APP_DATA_MAP, fh, default=datetime_json_handler)
        with open(cfg.COUNT_TRACKER, 'w') as fh:
            json.dump(MONTHLY_COUNT_TRACKER, fh)

    if is_last_day_of_month():
        os.unlink(cfg.COUNT_TRACKER)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool for checking updates for certain applications.')
    parser.add_argument('-a', '--app', help='Check updates for a specific application.', required=False, default=None)

    args = parser.parse_args()
    application = None

    if args.app:
        LOGGER.info('Checking updates only for the application: {app}'.format(app=args.app))
        application = args.app
    main(application)
