# coding: utf-8

import argparse


class ArgumentParser(object):
    def __init__(self, description=""):
        self._parser = argparse.ArgumentParser(description=description)
        self._arguments = None

    def parse_args(self):
        if self._arguments is None:
            self._arguments = self._parser.parse_args()

    def __getattr__(self, item):
        if hasattr(self._arguments, item):
            return getattr(self._arguments, item)
        else:
            return getattr(self._parser, item)

    def __str__(self):
        return str(self._parser)


class ArgumentParseAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs, **kwargs):
        super(ArgumentParseAction, self).__init__(option_strings, dest, nargs, **kwargs)


argument_parser = ArgumentParser()
