from telebot import TeleBot, custom_filters
from telebot.handler_backends import State, StatesGroup
#from telebot.apihelper import ApiHTTPException, ApiTelegramException
from configparser import ConfigParser
import logging

from dbhandler import DBHandler
from utils import get_str, get_arr, list2enum, HELP_STR


# Setup logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Initialize bot and database
bot = TeleBot(get_str("telegram", "token"))
db = DBHandler()
logging.info(f"Using database '{db.uri}'")


class AddStates(StatesGroup):
    """Used for new piece processing"""
    source = State()
    ftype = State()
    names = State()
    checking = State()


def user_choice(msg, ops):
    """Check user input"""
    choice = msg.text
    if choice in ops:
        return choice
    elif choice.isdigit() and 1 <= int(choice) <= len(ops):
        return ops[int(choice) - 1]
    bot.send_message(msg.chat.id, "Please choose one of available options.")
    logging.info(f"{msg.from_user.id} - Bad option '{choice}'")
    return None


def send_long_msg(chat_id, text):
    """Send a message that might be too long"""
    bot.send_message(chat_id, text, parse_mode="Markdown")

@bot.message_handler(commands=["start", "help"])
def start_cmd(msg):
    """Help message"""
    logging.info(f"{msg.from_user.id} - Displayed help message")
    bot.send_message(msg.chat.id, f"Let me show thy path.\n{HELP_STR}")


@bot.message_handler(commands=["add"])
def add_command(msg):
    """Start adding new piece and ask for source"""
    bot.set_state(msg.from_user.id, AddStates.source, msg.chat.id)
    logging.info(f"{msg.from_user.id} - Adding new piece")
    sources_str = list2enum(get_arr("database", "sources"))
    bot.send_message(msg.chat.id,
        "Which set is this piece from? "
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


@bot.message_handler(state=AddStates.source)
def source_state(msg):
    """Handle source and ask for ftype"""
    source = user_choice(msg, get_arr("database", "sources"))
    if source is None:
        return
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data["source"] = source
    logging.info(f"{msg.from_user.id} - Recorded source '{source}'")
    
    ftypes_str = list2enum(get_arr("database", "ftypes"))
    bot.send_message(
        msg.chat.id,
        f"Now specify piece form type. Available options are:\n{ftypes_str}"
    )
    bot.set_state(msg.from_user.id, AddStates.ftype, msg.chat.id)


@bot.message_handler(state=AddStates.ftype)
def ftype_state(msg):
    """Handle ftype and ask for tile names"""
    ftype = user_choice(msg, get_arr("database", "ftypes"))
    if ftype is None:
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


@bot.message_handler(state=AddStates.checking, commands=["save"])
def save_command(msg):
    """Save data to database"""
    editors = [int(x) for x in get_arr("telegram", "editors")]
    if msg.from_user.id in editors:
        with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            db.add_tiles(data["names"], data["ftype"], data["source"])
        bot.send_message(msg.chat.id, "A new path to madness has emerged.")
        logging.info(f"{msg.from_user.id} - New piece added")
    else:
        bot.send_message(msg.chat.id, "Sorry, you are not in editors list.")
        logging.info(f"{msg.from_user.id} - Not in editors list")
    bot.delete_state(msg.from_user.id, msg.chat.id)


@bot.message_handler(commands=["list"])
def list_cmd(msg):
    """List all pieces in a database"""
    for ftype in get_arr("database", "ftypes"):
        results = db.list_pieces(ftype)
        send_long_msg(msg.chat.id, results)
    logging.info(f"{msg.from_user.id} - Listed all pieces")


@bot.message_handler(state=None)
def search_command(msg):
    """For stateless messages look up string in database"""
    results = db.find_tiles(msg.text)
    if not len(results):
        bot.send_message(msg.chat.id, f"Can't find '{msg.text}' tile.")
        logging.info(f"{msg.from_user.id} - Failed search")
        return
    send_long_msg(msg.chat.id, results)
    logging.info(f"{msg.from_user.id} - Successful search")


logging.info(f"Starting bot")
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling()
