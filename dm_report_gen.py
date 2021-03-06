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
bot._reset_user_group_map()
group_df = pd.read_sql('select * from dim_group;', bot.db_conn)
for idx, group in group_df.iterrows():
    group_id = group.get('group_id')
    group_name = group.get('group_name')
    group_code = group.get('group_code')
    group_rules = group.get('group_rules')
    # current_users = bot._sync_user_group(group_id, group_name, group_code)
    bot._sync_user_group(group_id, group_name, group_code)
    bot._open_group_chat(group_name, group_code)
    bot._send_chat(group_rules)
    # current_users = pd.read_sql(f'select user_id from instaDb where group_id = {group_id};', bot.db_conn)
    # current_users = list(current_users['user_id'])

    # df_group_user_post = pd.read_sql( f'''select * from dim_group_user_post''', bot.db_conn)
    # here are the latest posts
    # please show some love
    # I will announce defaulter results in a couple of hours
    _usr_df = pd.read_sql(f'''select user_id from instaDB
                                WHERE group_id = {group_id}
                                AND followers = {1}
                                ;''', bot.db_conn)
    current_users = list(_usr_df['user_id'].unique())
    for user_id in current_users:
        group_user_post_df = pd.read_sql(f'''select * from dim_group_user_post
            WHERE user_id="{user_id}"
            AND group_id={group_id}
            AND liked_by_all = {0}
            ORDER BY timestamp DESC;''', bot.db_conn)
        for idx, meta in group_user_post_df.iterrows():
            post_url = meta.get('post_url')
            bot._check_mutual_likes(group_id, user_id, post_url)

    # df_group_user_like = pd.read_sql(f'''select * from fact_group_user_like;''', bot.db_conn)

    df_group_user_post = pd.read_sql(f'''select * from dim_group_user_post
                                where group_id = {group_id}
                                AND liked_by_all = {0}
                                ;''', bot.db_conn)

    bot._open_group_chat(group_name, group_code)
    # TODO: chk why this behaves weird
    for post_url in list(df_group_user_post['post_url'].unique()):
        df_group_user_like = pd.read_sql(f'''select * from fact_group_user_like
            WHERE post_url="{post_url}" AND group_id = {group_id}
            AND bool_like=0;''', bot.db_conn)

        df_group_user_like_exist = pd.read_sql(f'''select * from fact_group_user_like
            WHERE post_url="{post_url}" AND group_id = {group_id}''', bot.db_conn)

        if df_group_user_like.empty and df_group_user_like_exist.empty:
            # TODO: why is data not being captured for these people?
            bot.text_to_speech(f"No data for post_url -> {post_url}")
            bot._delete_no_data_post(group_id, post_url)
        elif df_group_user_like.empty:
            txt_msg = f'''{post_url}
            Yay! everyone has participated in liking this post!
            Pease keep on showing same love to all the family members.
            '''
            bot._send_chat(txt_msg)
        else:
            txt_msg = f'''{post_url}
            Hello folks I have liked the above post,
            Requesting members listed below to please like it:
            '''
            for usr in df_group_user_like['user_id']:
                txt_msg += f" :-( @{usr}\n"
            bot._send_chat(txt_msg)
        time.sleep(randint(5, 10))

# bot.db_conn.commit("DELETE FROM dim_group")
#bot.db_conn.execute("DELETE FROM dim_group_user_post")
#bot.db_conn.execute("DELETE FROM fact_group_user_like")
