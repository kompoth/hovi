from configparser import ConfigParser
import os


HELP_STR = """
To search for tile in database just send me its name.

General commands:
/help, /start - get this message.
/add - start processing new piece.
/list - list all saved piece.

While processing:
/cancel - cancel processing.
/done - (when you are asked) stop adding tiles.
/save - (when you are asked) submit data to database.
"""
BOTPATH = os.path.dirname(os.path.realpath(__file__))
CFGPATH = os.path.join(BOTPATH, "config.ini")
DBPATH = os.path.join(BOTPATH, "db.sqlite")


def get_str(*args):
    """Get string value from configuration file"""
    config = ConfigParser()
    config.read(CFGPATH)
    return config.get(*args)


def get_arr(*args):
    """Get array from configuration file"""
    value = get_str(*args)
    return value.split(",")


def list2enum(arr: list):
    """Create an enumeration from a list"""
    str_list = [f"{i + 1}. {x}" for i, x in enumerate(arr)]
    return "\n".join(str_list)


def user_choice(choice, ops):
    """Check user input"""
    if choice in ops:
        return choice
    elif choice.isdigit() and 1 <= int(choice) <= len(ops):
        return ops[int(choice) - 1]
    return None


