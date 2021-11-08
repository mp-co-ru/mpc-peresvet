#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import logging.config
import tempfile
import os


LOG_LEVEL = logging.getLevelName(os.getenv("PRS_LOG_LEVEL"), logging.INFO)
TO_FILE = os.getenv("PRS_LOG_TO_FILE", 'True').lower() in ('true', '1', 't')

class PrsLogger:
    
    logger = None

    def __init__(self):
        log_file = (None, "peresvet.log")[TO_FILE]
        logging.basicConfig(filename=log_file, level=LOG_LEVEL)

class SmtLogger:
    """ Служба ведения логов приложения
    """
    __error_file = ''
    __logger = None
    __error_logger = None

    def __init__(self, error_log_file: str = None):
        self.__error_file = error_log_file or DEFAULT_FILE

        self.__logger = logging.getLogger('debug')
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.propagate = False
        debug_handler = logging.StreamHandler()
        debug_handler.setFormatter(
            logging.Formatter('%(asctime)s (%(levelname)s): %(message)s')
        )
        self.__logger.addHandler(debug_handler)

        self.__error_logger = logging.getLogger('smt_error')
        self.__error_logger.setLevel(logging.ERROR)
        self.__error_logger.propagate = False
        error_handler = logging.FileHandler(self.__error_file)
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s: %(message)s')
        )
        self.__error_logger.addHandler(error_handler)

    def get_error_log(self):
        return self.__error_file

    def debug(self, message, styles=None):
        if isinstance(styles, dict):
            message = style(message, styles)
        else:
            message = style(message, {'font': 'dim'})
        self.__logger.debug(message)

    def info(self, message, styles=None):
        if isinstance(styles, dict):
            message = style(message, styles)
        self.__logger.info(message)

    def warning(self, message, styles=None):
        if isinstance(styles, dict):
            message = style(message, styles)
        else:
            message = style(message, {'color': 'yellow'})
        self.__logger.warning(message)

    def error(self, message, styles=None):
        undecorated_message = message
        if isinstance(styles, dict):
            message = style(message, styles)
        else:
            message = style(message, {'color': 'red', 'font': 'bold'})
        self.__logger.error(message)
        self.__error_logger.error(undecorated_message, exc_info=False)

    def critical(self, message):
        self.__error_logger.critical(message, exc_info=True)


def style(message, styles=None):
    if styles is None:
        styles = {}

    ansi_styles = {
        'foreground': {
            'black': 30,
            'red': 31,
            'green': 32,
            'yellow': 33,
            'blue': 34,
            'magenta': 35,
            'cyan': 36,
            'white': 37,
            'reset': 39,
        },
        'background': {
            'black': 40,
            'red': 41,
            'green': 42,
            'yellow': 43,
            'blue': 44,
            'magenta': 45,
            'cyan': 46,
            'white': 47,
            'reset': 49,
        },
        'font': {
            'bold': 1,
            'dim': 2,
            'normal': 22,
        }
    }

    start = '\x1b[{color};{bgcolor};{font}m'.format(
        color=ansi_styles['foreground'][styles.get('color', 'reset')],
        bgcolor=ansi_styles['background'][styles.get('background-color', 'reset')],
        font=ansi_styles['font'][styles.get('font', 'normal')],
    )
    end = '\x1b[0m'

    return ''.join((start, str(message), end))
