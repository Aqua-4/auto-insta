"""
Start bot and perform activity
"""
from insta_ops import InstaOps
import pandas as pd
from random import randint, choice
import time


bot = InstaOps()
bot.account_init()

tags = list(pd.read_csv('insta_strings.csv').hashtags)


while(True):
    random_tag = choice(tags)
    bot.tagsearch_n_open(random_tag)
    bot.smart_activity(8)
    time.sleep(randint(2700, 3300))
