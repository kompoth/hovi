from configparser import ConfigParser
import os

BOTPATH = os.path.dirname(os.path.realpath(__file__))
CFGPATH = os.path.join(BOTPATH, "config.ini")
DBPATH = os.path.join(BOTPATH, "db.sqlite")


def str_opt(*args):
    """Get string value from configuration file"""
    config = ConfigParser()
    config.read(CFGPATH)
    return config.get(*args)


def list2enum(arr: list):
    """Create an enumeration from a list"""
    str_list = [f"{i + 1}. {x}\n" for i, x in enumerate(arr)]
    return "".join(str_list)
