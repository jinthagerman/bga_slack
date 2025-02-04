#!/usr/bin/env python3
"""Bot to create games on discord."""
import logging.handlers
import time
import traceback
import shlex

import random
from creds import USERNAME, PASSWORD, TABLE_ID, USERNAME_MAP, WEBHOOK_URL, ADDITIONAL_MESSAGES
from slack_sdk.webhook import WebhookClient
from bga_table_status import get_current_player
from bga_account import BGAAccount
from utils import send_help, force_double_quotes, saveListToFile, readListFromFile, pickRandomMessage
from bga_agricola import is_harvest_round

LOG_FILENAME = "errs"
logger = logging.getLogger(__name__)
logging.getLogger("slack").setLevel(logging.WARN)
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=0)
formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

bga_account = BGAAccount()
bga_account.login(USERNAME, PASSWORD)
player_id = bga_account.get_player_id(USERNAME)
tables_data = bga_account.get_tables(player_id)
table_data = tables_data[TABLE_ID]
previous_player = ""
progress, _, current_player_id, link = bga_account.get_table_metadata(table_data)
player_data = get_current_player(table_data, current_player_id)
current_player_name = player_data["fullname"]
current_player = USERNAME_MAP[current_player_name]
game_name = table_data["game_name"]

message_text = f':game_die: *<@{current_player}>, It\'s your turn!* <{link}|Link>'

other_message = False
if game_name == "agricola" and is_harvest_round(progress):
    logger.debug(f'############### This is a harvest round')
    message_text += "\nDon't forget food, this is a harvest round! :corn:"
    other_message = True

try:
    with open("current_player", "r") as text_file:
        previous_player = text_file.read().rstrip()
        for bga_name, slack_id in USERNAME_MAP.items():
            if slack_id == previous_player:
                previous_player_name = bga_name
                break
        if current_player_name != previous_player_name:
            logger.debug(f'--------------- previous_player was {previous_player_name}')
except FileNotFoundError:
    logger.debug("--------------- current_player file not found. Will create it")

if current_player != previous_player:
    logger.debug(f'+++++++++++++++ current_player is now {current_player_name}')
    with open("current_player", "w") as text_file:
        if not other_message:
            message_text += f"\n{pickRandomMessage(ADDITIONAL_MESSAGES)}"
        webhook = WebhookClient(WEBHOOK_URL)
        webhook.send(text=message_text)
        text_file.write(current_player)
else:
    logger.debug(f'+++++++++++++++ current_player is still {current_player_name}')
