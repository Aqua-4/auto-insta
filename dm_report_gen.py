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

# import platform

bot = InstaOps(False, False, True, True)

bot.account_init()


def _group_users_list(group_name, group_code):
    _open_group_chat(group_name, group_code)
    return _get_group_users()


def _sync_user_group(group_id, group_name, group_code):
    current_users = _group_users_list(group_name, group_code)
    for user in current_users:
        meta = bot._user_meta(user)
        bot._update_meta(user, meta)
        __map_user_group(user, group_id)
        bot._like_userpost(user, 1)
        post_url = bot.driver.current_url
        _sync_group_user_post(user, group_id, post_url, timestamp)
    return current_users


def _sync_group_user_post(user, group_id, post_url, timestamp):
    """
     user_id VARCHAR(30),
     group_id INT,
     post VARCHAR(80) NOT NULL,
     timestamp DATE,
    """
    db_conn.execute(f'''INSERT INTO
            dim_group_user_post(user_id,group_id,post,timestamp) Values
            ("{user}",{group_id},"{post_url}","{timestamp}");
        ''')


def __get_post_timestamp():
    timestamp = bot.driver.find_element_by_tag_name(
        "time").get_attribute("title")
    return datetime.strptime(timestamp, "%b %d, %Y").date()


def __map_user_group(user, group_id):
    bot.db_conn.execute(f'''UPDATE instaDB SET group_id = {group_id}
     where user_id="{user}";''')


def __reset_user_group_map():
    bot.db_conn.execute(f'''UPDATE instaDB SET group_id = {None};''')


def _open_group_chat(group_name, group_code):
    bot.driver.get(group_code)
    _href = group_code.split("instagram.com")[1]
    time.sleep(5)
    group_ele = bot.driver.find_element_by_xpath(f"//a[@href='{_href}']")
    group_ele.click()


def __click_group_info_icon():
    bot.driver.execute_script(
        '''return document.querySelector('button>svg[aria-label="View Thread Details"]')
        .parentElement.click();''')


def _get_group_users():
    __click_group_info_icon()
    members = bot.driver.find_elements_by_xpath("//div[@role='button']")
    usr_list = []
    for member in members:
        usr_id = member.find_element_by_tag_name("div").text.splitlines()[0]
        usr_list.append(usr_id)
    return usr_list


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
    __reset_user_group_map()
    current_users = _sync_user_group(group_id, group_name, group_code)
    for user in
    group_user_df = pd.read_sql('''select * from dim_group_user_post 
        where ;''', bot.db_conn)
