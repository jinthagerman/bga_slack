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
from utils import send_help, force_double_quotes

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
player_data = get_current_player(table_data)
current_player = USERNAME_MAP[player_data["fullname"]]
previous_player = ""
_, _, link = bga_account.get_table_metadata(table_data)

try:
    with open("current_player", "r") as text_file:
        previous_player = text_file.read().rstrip()
except FileNotFoundError:
    logger.debug("current_player file not found. Will create it")

if current_player != previous_player:
    with open("current_player", "w") as text_file:
        webhook = WebhookClient(WEBHOOK_URL)
        webhook.send(text=f':game_die: *<@{current_player}>, It\'s your turn!* <{link}|Link>\n{random.choice(ADDITIONAL_MESSAGES)}')
        text_file.write(current_player)
else:
    logger.debug(f'current_player is still {player_data["fullname"]}')
