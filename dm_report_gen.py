"""
Bot starts to like and comment on user post based on AI
Every successfull loop bot will be slowed down by 5 minutes
Incase the followers LESS than following then bot will automatically unfollow
"""
from insta_ops import InstaOps
import pandas as pd
from random import randint, choice
import time
from datetime import datetime
import platform


if platform.system() == 'Linux':
    bot = InstaOps(True, False, True)
else:
    bot = InstaOps(True)
bot.account_init()

"""
1. get all groups from dim_group
2. visit all groups -> map users to groups
3. reset user_map for against group_id & map users with group_id
4. for group
    1. get latest user post  from dim_group_user_post distinct by user
    2. get list of likes for the post
    3. highlight users from group who have not liked the post
"""

group_df = pd.read_sql('select * from dim_group;', bot.db_conn)
for idx, group in group_df.iterrows():
    group_id = group.get('group_id')
    group_name = group.get('group_name')
    group_code = group.get('group_code')
    group_rules = group.get('group_rules')
    # current_users = bot._sync_user_group(group_id, group_name, group_code)
    bot._sync_user_group(group_id, group_name, group_code)
    # current_users = pd.read_sql(f'select user_id from instaDb where group_id = {group_id};', bot.db_conn)
    # current_users = list(current_users['user_id'])

    # df_group_user_post = pd.read_sql( f'''select * from dim_group_user_post''', bot.db_conn)
    # here are the latest posts
    # please show some love
    # I will announce defaulter results in a couple of hours

    df_group_user_post = pd.read_sql(f'''select * from dim_group_user_post
                                where group_id = {group_id};''', bot.db_conn)
    current_users = list(df_group_user_post['user_id'])
    post_links = []
    for user_id in current_users:
        group_user_post_df = pd.read_sql(f'''select * from dim_group_user_post
            WHERE user_id="{user_id}"
            AND group_id={group_id}
            AND liked_by_all = {0}
            ORDER BY timestamp DESC;''', bot.db_conn)
        for idx, meta in group_user_post_df.iterrows():
            post_url = meta.get('post_url')
            post_links.append(post_url)
            bot._check_mutual_likes(group_id, user_id, post_url, current_users)

    # df_group_user_like = pd.read_sql(f'''select * from fact_group_user_like;''', bot.db_conn)

    bot._open_group_chat(group_name, group_code)
    # TODO: chk why this behaves weird
    for post_url in post_links:
        df_group_user_like = pd.read_sql(f'''select * from fact_group_user_like
            WHERE post_url="{post_url}" AND group_id = {group_id}
            AND bool_like=0;''', bot.db_conn)

        df_group_user_like_exist = pd.read_sql(f'''select * from fact_group_user_like
            WHERE post_url="{post_url}" AND group_id = {group_id}''', bot.db_conn)

        if df_group_user_like.empty and df_group_user_like_exist.empty:
            # TODO: why is data not being captured for these people?
            pass
        elif df_group_user_like.empty:
            txt_msg = f'''{post_url}
            Yay! everyone has participated in liking this post!
            Pease keep on showing same love to all the family members.
            '''
        else:
            txt_msg = f'''{post_url}
            Following are the like-defaulters for this post:
            '''
            for usr in df_group_user_like['user_id']:
                txt_msg += f" :-( @{usr}\n"
        bot._send_chat(txt_msg)
        time.sleep(randint(5, 10))

# bot.db_conn.commit("DELETE FROM dim_group")
#bot.db_conn.execute("DELETE FROM dim_group_user_post")
#bot.db_conn.execute("DELETE FROM fact_group_user_like")
