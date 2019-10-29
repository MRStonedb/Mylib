# coding: utf-8

from configparser import ConfigParser
from lib.argument_parser import argument_parser

configure_group = argument_parser.add_argument_group("configure")
configure_group.add_argument("-c", "--config", dest="config_path", default=None, help="set configure file path")


class Configure(object):
    def __init__(self, path):
        self.parser = ConfigParser()
        if argument_parser.config_path:
            self.parser.read(argument_parser.config_path)
        else:
            self.parser.read(path)

    def __getattr__(self, item):
        return getattr(self.parser, item)
