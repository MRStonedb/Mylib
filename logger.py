# coding: utf-8

import os
import logging
import logging.handlers
from lib.argument_parser import argument_parser, ArgumentParseAction


class LogLevelAction(ArgumentParseAction):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(LogLevelAction, self).__init__(option_strings, dest, nargs, **kwargs)
        self._level_dict = dict(debug=logging.DEBUG, info=logging.INFO, warning=logging.WARNING, error=logging.ERROR)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self._level_dict[values])


log_group = argument_parser.add_argument_group("logger")
log_group.add_argument("-l", "--log_level", dest="log_level", type=str,
                       choices=["debug", "info", "warning", "error"], action=LogLevelAction,
                       default=logging.INFO, help="set log level")
log_group.add_argument("-s", "--enable_console", dest="enable_console", type=bool,
                       default=False, help="enable console log")


class BaseLogger(object):
    def __init__(self):
        self._basic_logger = logging.getLogger("my")
        self._logger = self._basic_logger
        self._stream_handler = logging.StreamHandler()
        if argument_parser.enable_console:
            self._basic_logger.addHandler(self._stream_handler)
        self._basic_logger.setLevel(logging.NOTSET)

    def get_logger(self, name):
        logger = self._logger.getChild(name)
        return logger

    def __getattr__(self, item):
        return getattr(self._logger, item)


class DailyLogger(BaseLogger):
    def __init__(self, name, file_path, file_name, back_count,
                 log_format="%(asctime)-15s %(levelname)-10s %(message)s %(filename)s %(lineno)d"):
        super(DailyLogger, self).__init__()
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        self._logger = self._basic_logger.getChild(name)
        self._file_handler = logging.handlers.TimedRotatingFileHandler(filename=os.path.join(file_path, file_name),
                                                                       when='D',
                                                                       interval=1,
                                                                       backupCount=back_count)
        self._log_format = logging.Formatter(fmt=log_format)
        self._file_handler.setFormatter(self._log_format)
        self._logger.addHandler(self._file_handler)
        self._logger.setLevel(argument_parser.log_level)
