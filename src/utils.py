"""Utils for various parts of this program"""
from urllib.parse import urlparse
import re
import random
import logging
from logging.handlers import RotatingFileHandler

logging.getLogger("slack").setLevel(logging.WARN)

LOG_FILENAME = "errs"
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=0)
formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Via https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def saveListToFile(list, filename):
    with open(filename, "w") as text_file:
        for item in list:
            text_file.write(item + '\n')

def readListFromFile(filename):
    try:
        with open(filename, "r") as text_file:
            return text_file.read().splitlines()
    except FileNotFoundError:
        return []

def pickRandomMessage(ADDITIONAL_MESSAGES):
    RANDOM_MESSAGES_FILENAME = "random_messages"
    additional_messages = readListFromFile(RANDOM_MESSAGES_FILENAME)
    logger.debug(f'{len(additional_messages)}" messages left in {RANDOM_MESSAGES_FILENAME}')
    if len(additional_messages) == 0:
        logger.debug(f'Repopulating {RANDOM_MESSAGES_FILENAME} with responses')
        random.shuffle(ADDITIONAL_MESSAGES)
        additional_messages = ADDITIONAL_MESSAGES
    additional_message = additional_messages.pop(0)
    saveListToFile(additional_messages, RANDOM_MESSAGES_FILENAME)
    return additional_message

def reset_context(contexts, author):
    """End the current interactive session by deleting info about it."""
    contexts[author] = {}


async def send_help(message, help_type):
    """Send the user a help message from a file"""
    filename = "src/docs/" + help_type + "_msg.md"
    with open(filename) as f:
        text = f.read()
    remainder = text.replace(4 * " ", "\t")
    await send_message_partials(message.author, remainder)


async def send_message_partials(destination, remainder):
    # Loop over text and send message parts from the remainder until remainder is no more
    while len(remainder) > 0:
        chars_per_msg = 2000
        if len(remainder) < chars_per_msg:
            chars_per_msg = len(remainder)
        msg_part = remainder[:chars_per_msg]
        remainder = remainder[chars_per_msg:]
        # Only break on newline
        if len(remainder) > 0:
            while remainder[0] != "\n":
                remainder = msg_part[-1] + remainder
                msg_part = msg_part[:-1]
            # Discord will delete whitespace before a message
            # so preserve that whitespace by inserting a character
            while remainder[0] == "\n":
                remainder = remainder[1:]
            if remainder[0] == "\t":
                remainder = ".   " + remainder[1:]
        await destination.send(msg_part)


def normalize_name(game_name):
    return re.sub("[^a-z0-7]+", "", game_name.lower())


def force_double_quotes(string):
    # People from other countries keep on using strange quotes because of their phone's keyboard
    # Force double quotes so shlex parses correctly
    all_quotes = "'‹›«»‘’‚“”„′″「」﹁﹂『』﹃﹄《》〈〉"
    return re.sub("[" + all_quotes + "]", '"', string)
