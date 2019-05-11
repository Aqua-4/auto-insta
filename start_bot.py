"""
Start bot and perform activity
"""
from insta_ops import InstaOps
import pandas as pd
from random import randint, choice
import time


bot = InstaOps(False)
bot.account_init()

# Uncomment to update DB
# bot.sync_db()

tags_df = pd.read_excel('insta_config.xlsx', sheet_name='hashtags')
comm_df = pd.read_excel('insta_config.xlsx', sheet_name='comments')


tags = list(tags_df.hashtags)
comments = list(comm_df.comments)

while(True):
    random_tag = choice(tags)
    bot.tagsearch_n_open(random_tag)
    bot.smart_activity(5, 4, comments)
    time.sleep(randint(2700, 3300))
    if bot._user_meta(bot.user_id)["following"] > bot._user_meta(bot.user_id)["followers"]:
        bot.unfollow_bot_leads()
