"""
Show following Insights:
1. followers gained
2. algorithm accuracy
"""

from insta_ops import InstaOps
import pandas as pd
from random import randint, choice
import time


bot = InstaOps(False)
bot.account_init()

#bot.sync_db()
#bot.text_to_speech("DB synced")
bot.refresh_db()
bot.text_to_speech("DB refreshed")


