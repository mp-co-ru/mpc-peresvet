#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import logging.config
import tempfile
import os
import sys

LOG_LEVEL = logging.getLevelName(os.getenv("PRS_LOG_LEVEL", "INFO"))
TO_FILE = os.getenv("PRS_LOG_TO_FILE", 'False').lower() in ('true', '1', 't')
LOG_FILE_NAME = "peresvet.log"
LOG_RETENTION = os.getenv("PRS_LOG_RETENTION", "1 months")
LOG_ROTATION = os.getenv("PRS_LOG_ROTATION", "20 days")

from loguru import logger
import json


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id='app')
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level,record.getMessage())


class PrsLogger:

    @classmethod
    def make_logger(cls):

        logger = cls.customize_logging(
            logging_config.get('path') ,
            level=LOG_LEVEL,
            retention=LOG_RETENTION,
            rotation=logging_config.get('rotation'),
            format=logging_config.get('format')
        )
        return logger

    @classmethod
    def customize_logging(cls,
            filepath: Path,
            level: str,
            rotation: str,
            retention: str,
            format: str
    ):

        logger.remove()
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format
        )
        logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format
        )
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        for _log in ['uvicorn',
                     'uvicorn.error',
                     'fastapi'
                     ]:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

        return logger.bind(request_id=None, method=None)


    @classmethod
    def load_logging_config(cls, config_path):
        config = None
        with open(config_path) as config_file:
            config = json.load(config_file)
        return config







class PrsLogger(logging.Logger):
    """ Служба ведения логов приложения
    """
    def __init__(self, name):
        
        '''
        log_file = (None, LOG_FILE_NAME)[TO_FILE]
        logging.basicConfig(filename=log_file, level=LOG_LEVEL)

        self.__logger = logging.getLogger('peresvet')
        self.__logger.propagate = False
        handler = logging.StreamHandler(sys.)
            handler = logging.StreamHandler(sys.)
        if LOG_LEVEL == logging.DEBUG:
            format_str = "%(asctime)s : %(levelname)s : %(filename)s.%(funcName)s.%(lineno)d :: %(message)s"
        else:
            format_str = "%(asctime)s : %(levelname)s :: %(message)s"
        
        handler.setFormatter(
            logging.Formatter(format_str)
        )
        self.__logger.addHandler(handler)
        '''
        '''
        if TO_FILE:
            handler = logging.FileHandler(filename=LOG_FILE_NAME)
        else:
            handler = logging.StreamHandler(sys.stdout)
        
        if LOG_LEVEL == logging.DEBUG:
            format_str = "%(asctime)s : %(levelname)s : %(filename)s.%(funcName)s.%(lineno)d :: %(message)s"
        else:
            format_str = "%(asctime)s : %(levelname)s :: %(message)s"

        logging.basicConfig(
            level=LOG_LEVEL, 
            format=format_str,
            handlers=[handler]
        )

        self.__logger = logging.getLogger('peresvet')
        '''
        if TO_FILE:
            handler = logging.FileHandler(filename=LOG_FILE_NAME)
        else:
            handler = logging.StreamHandler(sys.stdout)
        
        if LOG_LEVEL == logging.DEBUG:
            format_str = "%(asctime)s : %(levelname)s : %(filename)s.%(funcName)s.%(lineno)d :: %(message)s"
        else:
            format_str = "%(asctime)s : %(levelname)s :: %(message)s"
        handler.setFormatter(logging.Formatter(format_str))
        self.handlers = [handler]

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

    def critical(self, message):
        self.__logger.critical(message, exc_info=True)

    def get_logger(self):
        return self.__logger

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
