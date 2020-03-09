"""
Bot starts to like and comment on user post based on AI
Incase the followers LESS than following then bot will automatically unfollow
"""
from insta_ops import InstaOps
import pandas as pd
from random import randint, choice
import time
import platform

if platform.system() == 'Linux':
    bot = InstaOps(True, False, True)
else:
    bot = InstaOps(True)
bot.account_init()


tags_df = pd.read_excel('insta_config.xlsx', sheet_name='hashtags')
comm_df = pd.read_excel('insta_config.xlsx', sheet_name='comments')


tags = list(tags_df.hashtags)
comments = list(comm_df.comments)

while(True):
    random_tag = choice(tags)
    bot._update_session_meta()
    bot.tagsearch_n_open(random_tag)
    bot.smart_activity(5, 4, comments, random_tag)
    time.sleep(randint(2700, 3300))
    bot.refresh_db()
    time.sleep(randint(3000, 6000))
    if (bot._user_meta(bot.user_id)["following"] + 100) < bot._user_meta(bot.user_id)["followers"]:
        bot.unfollow_bot_leads()
        time.sleep(randint(2700, 3300))
    bot._store_session_info()
