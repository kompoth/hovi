from configparser import ConfigParser
import os

HOVIPATH = os.path.dirname(os.path.realpath(__file__))
CFGPATH = os.path.join(HOVIPATH, "config.ini")
DBPATH = os.path.join(HOVIPATH, "db.sqlite")


def str_opt(*args):
    """Get string value from configuration file"""
    config = ConfigParser()
    config.read(CFGPATH)
    return config.get(*args)
