"""
Bot starts to like and comment on user post based on AI
Incase the followers LESS than following then bot will automatically unfollow
"""
from insta_ops import ..InstaOps
import pandas as pd
from random import choice
import platform

if platform.system() == 'Linux':
    bot = InstaOps(True, False, True)
else:
    bot = InstaOps(True)
bot.account_init()


tags_df = pd.read_excel('insta_config.xlsx', sheet_name='hashtags')
comm_df = pd.read_excel('insta_config.xlsx', sheet_name='comments')


comments = list(comm_df.comments)

hash_tag = "#instagram"
bot.tagsearch_n_open(hash_tag)
user = bot._extract_users_from_tile(1)[0]
user_meta = bot._user_meta(user)
bot._follow_user(user, hash_tag)
bot._like_userpost(user, 1)
bot._insert_comment(choice(comments))
bot._unfollow_user(user)
