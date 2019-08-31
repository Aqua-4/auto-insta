"""
Update/Insert user_meta into db
for Machine-Learning
"""
from insta_ops import InstaOps
import pandas as pd
from random import randint, choice
import time


bot = InstaOps(True)
bot.account_init()

# Uncomment to update DB
bot.sync_db()
bot.refresh_db()
