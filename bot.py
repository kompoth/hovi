from telebot import TeleBot, custom_filters
from telebot.handler_backends import State, StatesGroup
from configparser import ConfigParser
import logging

from dbhandler import DBHandler, LikeTileError

HELP_STR = """
To search a tile in database just send its name to me.

To save a new tile to my database use these commands:
/newtile - start processing a new tile.
/save - save a new tile to a database.
/cancel - cancel processing without saving.
"""

# Read configuration file
config = ConfigParser()
config.read("config.ini")
token = config.get("telegram", "token")
url = config.get("database", "url")
types = config.get("database", "types").split(",")
types_str = "".join([f"{i + 1}. {x}\n" for i, x in enumerate(types)])

# Setup logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Initialize bot and database
bot = TeleBot(token)
db = DBHandler(url)


class NewTileStates(StatesGroup):
    """Used for new tile processing"""
    tile_type = State()
    first_side = State()
    second_side = State()
    checking = State()


@bot.message_handler(commands=["start", "help"])
def start_cmd(msg):
    """Help message"""
    logging.info(f"Displayed help message: {msg.from_user.id}")
    bot.send_message(msg.chat.id, f"Let me show you thy path:\n{HELP_STR}")


@bot.message_handler(commands=["newtile"])
def newtile_command(msg):
    """Start new tile processing"""
    editors = [int(x) for x in config.get("telegram", "editors").split(",")]
    if msg.from_user.id not in editors:
        bot.send_message(
            msg.chat.id,
            "Sorry, you must be in editors list to add new tiles."
        )
        bot.delete_state(msg.from_user.id, msg.chat.id)
        logging.info(f"Rejected new tile request: {msg.from_user.id}")
        return

    bot.send_message(msg.chat.id, "So let us begin.")
    bot.set_state(msg.from_user.id, NewTileStates.first_side, msg.chat.id)
    bot.send_message(
        msg.chat.id,
        "I  consider that each tile has two sides.\n"
        "What is the name of the first one?"
    )
    logging.info(f"Adding new tile: {msg.from_user.id}")


@bot.message_handler(state="*", commands=["cancel"])
def cancel_command(msg):
    """Cancel new tile processing without saving data"""
    if bot.current_states.get_state(msg.from_user.id, msg.chat.id) is None:
        bot.send_message(msg.chat.id, "There is no rite to cancel anyway.")
    else:
        bot.send_message(msg.chat.id, "Alas! You can try later though.")
        bot.delete_state(msg.from_user.id, msg.chat.id)
    logging.info(f"Canceled new tile processing: {msg.from_user.id}")


@bot.message_handler(state=NewTileStates.first_side)
def first_side_handler(msg):
    """Process the first tile side name"""
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data["side1"] = msg.text
    bot.send_message(msg.chat.id, "Right, what is the second side name?")
    bot.set_state(msg.from_user.id, NewTileStates.second_side, msg.chat.id)
    logging.info(f"Recorded first side: {msg.from_user.id}")


@bot.message_handler(state=NewTileStates.second_side)
def second_side_handler(msg):
    """Process the second tile side name"""
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data["side2"] = msg.text

    bot.send_message(
        msg.chat.id,
        f"Now specify the tile type. Available options are:\n{types_str}"
    )
    bot.set_state(msg.from_user.id, NewTileStates.tile_type, msg.chat.id)
    logging.info(f"Recorded second side: {msg.from_user.id}")


@bot.message_handler(state=NewTileStates.tile_type)
def tile_type_handler(msg):
    """Process the tile type"""
    tile_type = ""
    if msg.text.isdigit() and len(types) > int(msg.text) - 1:
        tile_type = types[int(msg.text) - 1]
    elif msg.text in types:
        tile_type = msg.text
    else:
        bot.send_message(
            msg.chat.id,
            f"There is no '{msg.text}' type of tiles in this Universum. "
            "Please use one of options listed above or ask bot admin to "
            "add a new one.\n\nTile creation failed."
        )
        bot.delete_state(msg.from_user.id, msg.chat.id)
        logging.info(f"Bad tile type: {msg.from_user.id}")
        return

    data_str = ""
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data["ttype"] = tile_type
        data_str = f"Side names: {data['side1']}, {data['side2']}\n"
        data_str += f"Tile type: {data['ttype']}"
    bot.send_message(
        msg.chat.id,
        f"Let us check, if everything is right.\n\n{data_str}\n\n"
        "If something is wrong, use command /cancel.\n"
        "Otherwise use command /save."
    )
    bot.set_state(msg.from_user.id, NewTileStates.checking, msg.chat.id)
    logging.info(f"Checking tile before saving: {msg.from_user.id}")


@bot.message_handler(state=NewTileStates.checking, commands=["save"])
def save_command(msg):
    """Save new tile to database and finish processing"""
    try:
        with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            db.add_tile(data["side1"], data["side2"], data["ttype"])
    except LikeTileError as err:
        bot.send_message(msg.chat.id, f"{err}\nTile creation failed.")
        logging.info(f"Failed to create tile: {msg.from_user.id}")
    else:
        bot.send_message(msg.chat.id, "A new path to madness has emerged.")
        logging.info(f"Created new tile: {msg.from_user.id}")
    
    bot.delete_state(msg.from_user.id, msg.chat.id)


@bot.message_handler(state=None)
def search_command(msg):
    """For stateless messages look up string in database"""
    str_list = "".join([f"{x}\n" for x in db.get_tile(msg.text)])
    if len(str_list):
        bot.send_message(msg.chat.id,
                         f"Here is what I have found:\n{str_list}")
        logging.info(f"Successful search: {msg.from_user.id}")
    else:
        bot.send_message(msg.chat.id,
                         f"Can't find any tile with '{msg.text}' side.")
        logging.info(f"Failed search: {msg.from_user.id}")

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling()
