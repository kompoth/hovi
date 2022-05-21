from telebot import TeleBot, custom_filters
from telebot.handler_backends import State, StatesGroup
from configparser import ConfigParser
import logging

from dbhandler import DBHandler


# Setup logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Read config
config = ConfigParser()
config.read("config.ini")

# Initialize bot and database
bot = TeleBot(config.get("telegram", "token"))
db = DBHandler(config.get("database", "url"))

# Preload ftypes and sources
ftypes = config.get("database", "ftypes").split(",")
ftypes_str = "".join([f"{i + 1}. {x}\n" for i, x in enumerate(ftypes)])
sources = config.get("database", "sources").split(",")
sources_str = "".join([f"{i + 1}. {x}\n" for i, x in enumerate(sources)])


def user_choice(ch, ops):
    if ch in ops:
        return ch
    elif ch.isdigit() and 1 <= int(ch) <= len(ops):
        return ops[int(ch) - 1]
    return None


class AddStates(StatesGroup):
    """Used for new piece processing"""
    source = State()
    ftype = State()
    names = State()
    checking = State()


@bot.message_handler(commands=["start", "help"])
def start_cmd(msg):
    """Help message"""
    logging.info(f"{msg.from_user.id} - Displayed help message")
    bot.send_message(msg.chat.id, "Let me show you thy path")


@bot.message_handler(commands=["add"])
def add_command(msg):
    """Start adding new piece and ask for source"""
    bot.set_state(msg.from_user.id, AddStates.source, msg.chat.id)
    logging.info(f"{msg.from_user.id} - Adding new piece")
    bot.send_message(msg.chat.id,
        "Which set is this piece from?"
        f"Available options are:\n{sources_str}")


@bot.message_handler(state="*", commands=["cancel"])
def cancel_command(msg):
    """Cancel adding without saving data"""
    if bot.current_states.get_state(msg.from_user.id, msg.chat.id) is None:
        bot.send_message(msg.chat.id, "Nothing to cancel.")
        logging.info(f"{msg.from_user.id} - Extra cancel request")
        return
    bot.send_message(msg.chat.id, "Alas! You can try later though.")
    bot.delete_state(msg.from_user.id, msg.chat.id)
    logging.info(f"{msg.from_user.id} - Cancel request")


@bot.message_handler(state=AddStates.names, commands=["done"])
def done_command(msg):
    """Stop reading names and proceed"""
    if bot.current_states.get_state(msg.from_user.id, msg.chat.id) is None:
        bot.send_message(msg.chat.id, "No recorded data.")
        logging.info(f"{msg.from_user.id} - Extra done request")
        return
    check_str = "Saving following data:\n\n"
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        check_str += f"*Source*: {data['source']}\n*Type*: {data['ftype']}"
        check_str += "\n*Tiles*:\n"
        check_str += "".join([f"\t{x}\n" for x in data["names"]])
    bot.send_message(msg.chat.id, check_str + "\nSend /save or /cancel.",
                     parse_mode="Markdown")
    bot.set_state(msg.from_user.id, AddStates.checking, msg.chat.id)
    logging.info(f"{msg.from_user.id} - Checking data")


@bot.message_handler(state=AddStates.checking, commands=["save"])
def save_command(msg):
    """Save data to database"""
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        db.add_tiles(data["names"], data["ftype"], data["source"])
    bot.send_message(msg.chat.id, "A new path to madness has emerged.")
    logging.info(f"{msg.from_user.id} - New piece added")
    bot.delete_state(msg.from_user.id, msg.chat.id)


@bot.message_handler(state=AddStates.source)
def source_state(msg):
    """Handle source and ask for ftype"""
    source = user_choice(msg.text, sources)
    if source is None:
        bot.send_message(msg.chat.id, "Please choose from the above list.")
        logging.info(f"{msg.from_user.id} - Bad source '{msg.text}'")
        return
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data["source"] = source
    logging.info(f"{msg.from_user.id} - Recorded source '{source}'")

    bot.send_message(
        msg.chat.id,
        f"Now specify piece form type. Available options are:\n{ftypes_str}"
    )
    bot.set_state(msg.from_user.id, AddStates.ftype, msg.chat.id)


@bot.message_handler(state=AddStates.ftype)
def ftype_state(msg):
    """Handle ftype and ask for tile names"""
    ftype = user_choice(msg.text, ftypes)
    if ftype is None:
        bot.send_message(msg.chat.id, "Please choose from the above list.")
        logging.info(f"{msg.from_user.id} - Bad ftype '{msg.text}'")
        return
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data["ftype"] = ftype
        data["names"] = []
    logging.info(f"{msg.from_user.id} - Recorded ftype '{ftype}'")
    
    bot.send_message(
        msg.chat.id,
        "Now send names of all tiles on this piece in separate messages."
    )
    bot.set_state(msg.from_user.id, AddStates.names, msg.chat.id)


@bot.message_handler(state=AddStates.names)
def names_state(msg):
    """Hande tile name and ask for more"""
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data["names"].append(msg.text)
    bot.send_message(msg.chat.id,
        f"Recorded name '{msg.text}'. When you are done send /done."
    )
    logging.info(f"{msg.from_user.id} - Recorded name '{msg.text}'")


@bot.message_handler(state=None)
def search_command(msg):
    """For stateless messages look up string in database"""
    results = db.get_tile(msg.text)
    if not len(results):
        bot.send_message(msg.chat.id, f"Can't find '{msg.text}' tile.")
        logging.info(f"{msg.from_user.id} - Failed search")
        return
    results_str = "".join([f"{x}\n" for x in results])
    bot.send_message(msg.chat.id, "Search results:\n" + results_str)
    logging.info(f"{msg.from_user.id} - Successful search")


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling()
