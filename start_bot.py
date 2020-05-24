"""
Bot starts to like and comment on user post based on AI
Every successfull loop bot will be slowed down by 5 minutes
Incase the followers LESS than following then bot will automatically unfollow
"""
from insta_ops import InstaOps
import pandas as pd
from random import randint, choice
import time
import platform

if platform.system() == 'Linux':
    bot = InstaOps(False, False, True)
else:
    bot = InstaOps(False)
bot.account_init()


tags_df = pd.read_excel('insta_config.xlsx', sheet_name='hashtags')
comm_df = pd.read_excel('insta_config.xlsx', sheet_name='comments')


tags = list(tags_df.hashtags)
comments = list(comm_df.comments)

# 1800 secs = 30 minutes
slow_down = 0
for _ in range(randint(2, 7)):
    random_tag = choice(tags)
    bot._update_session_meta()
    bot.tagsearch_n_open(random_tag)
    bot.smart_activity(5, 4, comments, random_tag)
    time.sleep(randint(900+slow_down, 1800+slow_down))
    bot.refresh_db()
    time.sleep(randint(900+slow_down, 1800+slow_down))
    bot._store_session_info()
    if (bot._user_meta(bot.user_id)["following"] - 100) > bot._user_meta(bot.user_id)["followers"]:
        bot.unfollow_bot_leads()
        time.sleep(randint(900+slow_down, 1800+slow_down))
    slow_down += 300  # slow down bot by 5 minutes
bot.text_to_speech("Bot has successfully completed all operations for the day")
