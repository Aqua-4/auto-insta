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
from selenium.common.exceptions import NoSuchElementException

# import platform

bot = InstaOps(False, False, True, True)

bot.account_init()


def _group_users_list(group_name, group_code):
    _open_group_chat(group_name, group_code)
    return _get_group_users()


def _sync_user_group(group_id, group_name, group_code):
    current_users = _group_users_list(group_name, group_code)
    current_users.remove("Search")
    current_users.remove(bot.user_id)
    for user in current_users:
        meta = bot._user_meta(user)
        bot._update_meta(user, meta)
        __map_user_group(user, group_id)
        try:
            bot._like_userpost(user, 1)
            # bot._InstaOps__open_first_userpost()
            post_url = bot.driver.current_url
            post_stamp = __get_post_timestamp()
            _sync_group_user_post(user, group_id, post_url, post_stamp)
        except:
            print(f"ERR:{user}")
            current_users.remove(user)
    return current_users


def _check_mutual_likes(group_id, user_id, post_url, current_users):
    """
    open post-likes-list
    scroll through users - if users completed stop scrolling and update all_like as 1
    """
    bot.driver.get(post_url)
    liked_list = _get_likes_list()
    current_users.remove(user_id)
    intersect = list(set(liked_list) & set(current_users))
    if set(intersect) == set(current_users):
        bot.db_conn.execute(f'''UPDATE dim_group_user_post
                    SET liked_by_all=1 WHERE post_url="{post_url}"''')
    not_liked_by = list(set(current_users) - set(intersect))
    _update_group_user_like(group_id, post_url, current_users, not_liked_by)


def _update_group_user_like(group_id, post_url, current_users, not_liked_by):
    """
        fact_group_user_like
         (post_url VARCHAR(80),
         group_id INT,
         user_id VARCHAR(30),
         bool_like INT DEFAULT 0
    """
    for user_id in current_users:
        bool_like = int(user_id not in not_liked_by)

        if pd.read_sql(f'''select * from fact_group_user_like
            WHERE post_url="{post_url}"
                AND group_id = {group_id}
                AND user_id = "{user_id}"
        ''', bot.db_conn).empty:
            bot.db_conn.execute(f'''INSERT INTO
                 fact_group_user_like(post_url,group_id ,user_id ,bool_like)
                 Values
                 ("{post_url}",{group_id},"{user_id}",{bool_like});
            ''')
        else:

            bot.db_conn.execute(f'''UPDATE fact_group_user_like
             SET bool_like = {bool_like}
             WHERE
                 post_url="{post_url}"
                 AND group_id={group_id}
                 AND user_id="{user_id}";
            ''')
    #    df_group_user_like = pd.read_sql('select * from fact_group_user_like;', bot.db_conn)


def _get_likes_list():

    time.sleep(randint(3, 6))
    total_count = __likes_count()
    __click_expand_likes_btn()
    dialog = bot.driver.find_element_by_xpath("//div/div[@role='dialog']")
    #    x=dialog.find_elements_by_xpath("//a[@title][@href]")
    #    y= dialog.find_elements_by_xpath("//div[@aria-labelledby][@class]")

    main_list = []
    li_cnt = 0
    prev_cnt = 0

    exit_counter = 0
    time.sleep(randint(3, 6))

    while(li_cnt <= total_count and exit_counter <= 5):
        prev_cnt = li_cnt

        try:
            li_list = dialog.find_elements_by_xpath("//a[@title][@href]")
            main_list.extend([a.text for a in li_list])
            main_list = list(set(main_list))
            li_list[-1].location_once_scrolled_into_view
        except:
            li_list[-2].location_once_scrolled_into_view

        li_cnt = len(main_list)
        time.sleep(randint(1, 3))
        if li_cnt == prev_cnt:
            # print(f"{li_cnt}<->{prev_cnt}")
            exit_counter += 1
            time.sleep(randint(3, 6))
        else:
            exit_counter = 0

    return main_list


def __likes_count():
    #    why would I handle for 1 or 2 likes
    exp_btn = __get_expand_likes_btn()
    return int(exp_btn.text.replace(' others', ''))+1


def __click_expand_likes_btn():
    #    return btn or false
    for btn in bot.driver.find_elements_by_xpath("//button[@type='button']"):
        if ' others' in btn.text:
            btn.click()
            break
    else:
        raise NoSuchElementException


def __get_expand_likes_btn():
    for btn in bot.driver.find_elements_by_xpath("//button[@type='button']"):
        if ' others' in btn.text:
            return btn
    else:
        raise NoSuchElementException


def _sync_group_user_post(user, group_id, post_url=None, timestamp=None):
    """
     user_id VARCHAR(30),
     group_id INT,
     post_url VARCHAR(80) NOT NULL,
     timestamp DATE,
    """
    if pd.read_sql(f'''select * from dim_group_user_post
     WHERE post_url="{post_url}"''', bot.db_conn).empty:
        bot.db_conn.execute(f'''INSERT INTO
                    dim_group_user_post(user_id, group_id, post_url, timestamp) Values
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
    bot.db_conn.execute(f'''UPDATE instaDB SET group_id = "{None}";''')


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
    # current_users = pd.read_sql(f'select user_id from instaDb where group_id = {group_id};', bot.db_conn)
    # current_users = list(current_users['user_id'])

    for user_id in current_users:
        group_user_post_df = pd.read_sql(f'''select * from dim_group_user_post
            WHERE user_id="{user_id}"
            ORDER BY timestamp DESC;''', bot.db_conn)
        latest_meta = group_user_post_df.iloc[0]
        post_url = latest_meta.get('post_url')
        _check_mutual_likes(group_id, user_id, post_url, current_users)
