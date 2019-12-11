# -*- coding: utf-8 -*-
"""Logger module."""
import logging


def get_logger(level=logging.DEBUG):
    """
    Function to return the logger object handle.

    :param: None
    :return: object
        The logger handle object.
    """
    logger = logging.getLogger('app-updates-checker')
    # Work as a stand-alone logger when other loggers are not available.
    if not logger.handlers:
        formatter = logging.Formatter(
            '[%(asctime)s]: %(name)s: %(levelname)s: %(message)s : %(filename)s#%(lineno)d %(funcName)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)
    # Disable duplicate logging. https://docs.python.org/2/library/logging.html#logger-objects
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    return logger
