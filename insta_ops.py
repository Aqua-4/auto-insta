# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 01:47:07 2018

@author: Parashar
-----------------------------------------------------------------------
All Instagram Operations
"""

from selenium import webdriver
from fake_useragent import UserAgent
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime
import logging
from os import path, remove
import pyttsx3
import platform
from random import randint, choice, shuffle
import sqlite3
from sklearn.externals import joblib
import time

logging.basicConfig(filename='auto_insta.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.getLogger().addHandler(logging.StreamHandler())


class InstaOps:

    def __init__(self, headless=True, rand_agent=False, bool_mute=False, incognito=False):
        """
        1. setup db_connection
        2. get all user info
        3. init chromedriver and TTS engine
        """

        self.db_conn = sqlite3.connect('auto-insta.db')
        self.user_id = pd.read_sql(
            "select user_id from creds", self.db_conn).user_id[0]

        options = webdriver.ChromeOptions()
        chromedata = pd.read_sql(
            "select chromedata from creds", self.db_conn).chromedata[0]
        options.add_argument("--start-maximized")
        options.add_argument("disable-infobars")
        options.add_experimental_option(
            "excludeSwitches", ['enable-automation'])
        self.headless = headless
        self.bool_mute = bool_mute
        if headless:
            options.add_argument("--headless")

        userAgent = """Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36
         (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36"""
        if rand_agent:
            ua = UserAgent()
            userAgent = ua.random
        options.add_argument(f'user-agent={userAgent}')
        # TODO: fix user agent to macbook

        self.incognito = incognito
        if chromedata and not incognito:
            options.add_argument('user-data-dir={}'.format(chromedata))

        exec_path = "chromedriver"
        if platform.system() == 'Linux':
            exec_path = "./chromedriver"

        self.driver = webdriver.Chrome(
            executable_path=exec_path, options=options)

        if not bool_mute:
            self.engine = pyttsx3.init()

        # load the model if exists
        if path.isfile('classifier_mod.pkl') and path.isfile('sc_X_mod.pkl'):
            self.classifier_mod = joblib.load('classifier_mod.pkl')
            self.sc_X = joblib.load('sc_X_mod.pkl')
            self.text_to_speech("Using Machine Learning for predictions")
        else:
            self.text_to_speech(
                "Contact developer for Machine Learning support and improve predictions")
            self.classifier_mod = False

        self.text_to_speech("Insta Bot has been initialized")

    def __del__(self):
        """
        chcek if smart_activity has been started
        if yes - check if session info has been stored
        """
        if not self.incognito:
            self._store_session_info()
        self.db_conn.commit()
        self.db_conn.close()
        self.text_to_speech("Shutting Down Instagram Bot", False)
        self.driver.quit()
        if not self.incognito:
            self.text_to_speech(
                "Bot has been powered off, goodbye {}".format(self.user_name), False)

    def account_init(self):
        """
        1. login to insta
        2. get/set user_name
        3. insert/update instaDB wrt followers and following
        """
        self._insta_login()
        usr_name = pd.read_sql(
            "select user_name from creds", self.db_conn).user_name[0]
        if not usr_name:
            self.user_name = self.__get_usr_name(self.user_id)
        else:
            self.user_name = usr_name

        login_greet = "Welcome {}, you have been logged into your account and ".format(
            self.user_name)
        login_greet += "here are your stats for the current session "
        self.text_to_speech(login_greet, False)
        self.follower_cnt = self.__get_number_of(
            "https://www.instagram.com/{}/followers/".format(self.user_id))
        self.following_cnt = self.__get_number_of(
            "https://www.instagram.com/{}/following/".format(self.user_id))
        self._session_stats(self.follower_cnt, self.following_cnt, True)

    def sync_db(self):
        # update the user profile
        self._sync_db_col("followers")
        self._sync_db_col("following")

    def refresh_db(self, limit=True):
        """
        Update the entries by stalking all of the users in the db
        use timestamp to support resume capability incase this function fails
        """
        sql_lim = " LIMIT {} ".format(randint(25, 50)) if limit else ""
        users = pd.read_sql("""select user_id from instaDB where
         (followers=1 OR following=1) AND
         acc_status=1 AND
         (timestamp IS IFNULL(NULL,0) OR
          followers_cnt IS IFNULL(NULL,0) AND
          following_cnt IS IFNULL(NULL,0) AND
          posts IS IFNULL(NULL,0)){};""".format(sql_lim), self.db_conn).user_id
        _err_cnt = 0
        _max = 3
        for user in users:
            try:
                meta = self._user_meta(user)
                self._update_meta(user, meta, True)
                _err_cnt = 0
            except:
                self.text_to_speech(
                    "User {} has been removed by insta".format(user))
                self.db_conn.execute('''UPDATE instaDB
                    SET acc_status=0 WHERE user_id="{usr}";
                '''.format(usr=user))
                _max = _max+1 if _max < 60 else 3
                _err_cnt += 1
            time.sleep(randint(2, _max))

            # TODO: TEST
            # print(_max, _err_cnt)
            if _err_cnt > 10:
                self.text_to_speech("Bot has been detected, refresh later")
                break

        self.text_to_speech("""Database has been refreshed.
            All user account have been synced""")

    def smart_activity(self, user_count=6, per_user_like=4, comments=[], hash_tag="#parashar"):
        """
        1. get list of users
        2. update meta for user
        3. predict if user will follow_back
        4. follow and like if precited that user will follow
        """
        # get 3 times the user_name incase of worst case scenario
        usr_counter = 0
        users = self._extract_users_from_tile(user_count*2)
        shuffle(users)
        for user in users:
            # try:
            user_meta = self._user_meta(user)
            self._update_meta(user, user_meta)
            if self.__predict(user_meta):
                self._follow_user(user, hash_tag)
                self._like_userpost(user, randint(
                    per_user_like/2, per_user_like))
                # TODO: find the optimal place to put this
                usr_counter += 1
                if comments:
                    self._insert_comment(choice(comments))
            else:
                self.text_to_speech(
                    "Algorithm predicts that user {} won't follow back".format(user), False)
            if usr_counter > user_count:
                break
            # except Exception:
            #           self.driver.current_url)
            #     self.account_init()

    def unfollow_bot_leads(self, fu_all=False):
        # unfollow users that don't follow back and were followed by this bot
        self.text_to_speech("Unfollowing users followed by bot")
        traitors = list(pd.read_sql("""select user_id from instaDb
         WHERE bot_lead=1 and following=1 and followers=0
         ORDER BY timestamp LIMIT 0,100;""", self.db_conn).user_id)
        _max = len(traitors) if fu_all else randint(25, 50)
        for usr in traitors[:_max]:
            self._unfollow_user(usr)
        self.text_to_speech("Unfollowed users that don't follow back")

    def unfollow_unfollowers(self):
        """
        Unfollow people who dont follow you back
        1. select user_id where followers=0
        2. unfollow(user_id) and updateDB
        """
        traitors = pd.read_sql(
            "select user_id from instaDB where followers=0", self.db_conn)
        traitors = list(traitors.user_id)
        self.text_to_speech(
            "Unfollowing users those who don't follow you", False)
        for traitor in traitors:
            self._unfollow_user(traitor)
        self.text_to_speech("Unfollowed unfollowers completed")
        # TODO: replace with fn
        self.follower_cnt = self.__get_number_of(
            "https://www.instagram.com/{}/followers/".format(self.user_id))
        self.following_cnt = self.__get_number_of(
            "https://www.instagram.com/{}/following/".format(self.user_id))
        self._session_stats(self.follower_cnt, self.following_cnt)

    def tagsearch_n_open(self, tag_name="#parashar"):
        """
        1. search for a hash-tag
        2. open the first photo tile
        """
        self.text_to_speech("searching for tag {}".format(tag_name))
        self.__search_tag(tag_name)
        try:
            self.__open_first_tile()
        except Exception as e:
            logging.error(e, exc_info=True)
            self.text_to_speech(
                "Tag search and open failed for {}".format(tag_name))


# --------------_______________________SEMI-Private Func_________________________-------------------

    def _bool_check_tag(self, tag_name="#parashar"):
        """
        1. search for a hash-tag
        2. open the first photo tile
        3. IF exception hashtag does not exist
        """
        self.__search_tag(tag_name)
        try:
            self.__open_first_tile()
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    def _get_missing_meta_users(self, limit=False):
        """
        Update the entries by stalking all of the users in the db
        use timestamp to support resume capability incase this function fails
        """
        sql_lim = " LIMIT {} ".format(randint(25, 50)) if limit else ""
        users = pd.read_sql("""select user_id from instaDB where
         (followers=1 OR following=1) AND
         acc_status=1 AND
         (timestamp IS IFNULL(NULL,0) OR followers_cnt IS IFNULL(NULL,0) AND
          following_cnt IS IFNULL(NULL,0) AND
          posts IS IFNULL(NULL,0)){};""".format(sql_lim), self.db_conn).user_id

        return users

    def _insta_login(self):
        # enter credentials if not logged in
        self.driver.get(
            "https://www.instagram.com/accounts/login/?source=auth_switcher")

        if self.driver.current_url != "https://www.instagram.com/":
            time.sleep(5)
            user_id = self.driver.find_element_by_xpath(
                '//input[@name="username"]')
            user_id.clear()
            user_id.send_keys(self.user_id)
            passwd = self.driver.find_element_by_xpath(
                '//input[@name="password"]')
            passwd.clear()
            passwd.send_keys(pd.read_sql(
                "select passwd from creds", self.db_conn).passwd[0])
            passwd.send_keys(Keys.RETURN)
            time.sleep(10)

    def _session_stats(self, session_follower_cnt, session_following_cnt, session_init=False):
        # announce session stats

        follower_cnt = self.__get_number_of(
            "https://www.instagram.com/{}/followers/".format(self.user_id))
        following_cnt = self.__get_number_of(
            "https://www.instagram.com/{}/following/".format(self.user_id))

        self.text_to_speech("Your current follower count is {}".format(
            follower_cnt), True, session_init)
        self.text_to_speech("You are now following {} people".format(
            following_cnt), session_init, session_init)
        if session_follower_cnt - follower_cnt != 0 and not session_init:
            diff = follower_cnt - session_follower_cnt
            lose_gain = "gained" if diff > 0 else "lost"
            self.text_to_speech(
                "You have {} {} followers".format(lose_gain, abs(diff)))

    def _update_session_meta(self):
        """
        store current session followers and following count
        will be called before starting smart_activity
        """
        self.follower_cnt = self.__get_number_of(
            "https://www.instagram.com/{}/followers/".format(self.user_id))
        self.following_cnt = self.__get_number_of(
            "https://www.instagram.com/{}/following/".format(self.user_id))
        self.session_stamp = str(datetime.now())

    def _store_session_info(self):
        try:
            follower_cnt = self.__get_number_of(
                "https://www.instagram.com/{}/followers/".format(self.user_id))
            following_cnt = self.__get_number_of(
                "https://www.instagram.com/{}/following/".format(self.user_id))
            delta_follower = follower_cnt - self.follower_cnt
            delta_following = following_cnt - self.following_cnt
            start_stamp = self.session_stamp
            end_stamp = str(datetime.now())
            self.db_conn.execute('''INSERT INTO
            smartlog(session_start, session_end, followers_cnt, following_cnt,
            delta_followers_cnt, delta_following_cnt )
            Values ("{start}","{end}",{foc},{fic},{dfoc},{dfic}
            );'''.format(start=start_stamp, end=end_stamp, foc=self.follower_cnt,
                         fic=self.following_cnt, dfoc=delta_follower,
                         dfic=delta_following))
        except Exception as e:
            logging.error(e, exc_info=True)
            self.text_to_speech("Failed to store session info")

    def _sync_db_col(self, column="followers"):
        """
            save column-list temporarily as checkpoint incase op
            if success: delte tmp file
            else: list will be generated from the csv, not from insta
        """
        # sync db column - followers/following

        tmp_file = "tmp_{fol_col}.csv".format(fol_col=column)
        if path.isfile(tmp_file):
            tmp_df = pd.read_csv(tmp_file)
            col_list = list(tmp_df['followers'])
        else:
            col_list = self.__get_list_of(column)
            tmp_df = pd.DataFrame({column: col_list})
            tmp_df.to_csv(tmp_file, index=False)

        self.db_conn.execute('''UPDATE instaDB
         SET {fol_col} = 0;'''.format(fol_col=column))

        for user in col_list:
            if pd.read_sql('select * from instaDB where user_id="{}"'.format(user), self.db_conn).empty:
                self.db_conn.execute('''INSERT INTO instaDB(user_id,{fol_col},acc_status)
                 Values ("{usr}",1,1);'''.format(fol_col=column, usr=user))
            else:
                self.db_conn.execute('''UPDATE instaDB  SET
                 {fol_col} = 1,
                 acc_status = 1
                 WHERE user_id = "{usr}";'''.format(fol_col=column, usr=user))
        self.db_conn.commit()
        # remove(tmp_file)
        self.text_to_speech("Column {} has been synced with DB".format(column))

    def _unfollow_user(self, u_name):
        # goto user_profile and unfollow
        insta_link = self.__format_userid(u_name)
        self.driver.get(insta_link)
        time.sleep(randint(5, 10))
        timestamp = datetime.now().date()

        if len(self.driver.find_elements_by_tag_name("h2")):
            self.db_conn.execute('''UPDATE instaDB SET acc_status=0, timestamp="{t_stamp}"
             where user_id="{usr}"'''.format(usr=u_name, t_stamp=timestamp))

            self.text_to_speech(
                "User {} acc does not exist anymore".format(u_name), False)
        else:
            self.__click_unfollow(u_name)
            self.db_conn.execute('''UPDATE instaDB SET following=0, timestamp="{t_stamp}"
             where user_id="{usr}"'''.format(usr=u_name, t_stamp=timestamp))

    def _extract_users_from_tile(self, user_count=20):
        # return list of usernames
        _list = []
        while len(_list) < user_count:
            try:
                _list.append(self.__get_tile_username())
            except Exception as e:
                logging.error(e, exc_info=True)
                self.text_to_speech("Cannot get user_name")
            click_right = self.driver.find_element_by_xpath('/html/body')
            click_right.send_keys(Keys.RIGHT)
            # unique list of user_names
            _list = list(set(_list))
            time.sleep(randint(4, 10))
        return _list

    def _update_meta(self, user, user_meta, refresh_mode=False):
        foc = user_meta['followers']
        fic = user_meta['following']
        posts = user_meta['posts']
        timestamp = datetime.now().date()
        if pd.read_sql('select * from instaDB where user_id="{}"'.format(user), self.db_conn).empty:
            self.db_conn.execute('''INSERT INTO
             instaDB(user_id,followers_cnt,following_cnt,posts,acc_status,bot_lead,timestamp) Values
             ("{usr}",{followers},{following},{posts},1,1,"{timestamp}");
            '''.format(usr=user, followers=foc, following=fic, posts=posts, timestamp=timestamp))
        elif refresh_mode:
            self.db_conn.execute('''UPDATE instaDB
                SET following_cnt={following}, followers_cnt={followers},
                posts={posts}, acc_status=1, timestamp="{timestamp}" WHERE user_id="{usr}";
            '''.format(usr=user, followers=foc, following=fic, posts=posts, timestamp=timestamp))
        else:
            self.db_conn.execute('''UPDATE instaDB
             SET following_cnt={following}, followers_cnt={followers},
             posts={posts}, acc_status=1, bot_lead=1, timestamp="{timestamp}" WHERE user_id="{usr}";
            '''.format(usr=user, followers=foc, following=fic, posts=posts, timestamp=timestamp))
        self.db_conn.commit()

    def _user_meta(self, u_name):
        """
        collects demographic meta
        return count of followers, following, posts
        """
        meta = {}
        user_url = self.__format_userid(u_name)
        meta['followers'] = self.__get_number_of(
            "{}followers/".format(user_url))
        meta['following'] = self.__get_number_of(
            "{}following/".format(user_url))
        meta['posts'] = self.__get_number_of(
            "{}posts/".format(user_url))
        logging.info("{} Meta-> {}".format(u_name, meta))
        return meta

    def _user_meta_deep(self, u_name):
        """
        TODO: WIP
        collects psychographic meta
        cr8 another class
            - variables will be availabe
            - seperate INIT & DEL
            -

        class =>
            - isntantiate selenium
            - hit isnta api
            - scroll through posts for location, avg_post_time, hashtags,

        function =>
            - open x number of tabs all at once
            - set(hashtags)
            - max(location)
            return these

        """

        pass

    def _like_userpost(self, user, count=0):
        """
        1. Navigate to user profile
        2. Like n number of posts
        """
        if self.driver.current_url != self.__format_userid(user):
            self.driver.get(self.__format_userid(user))
        time.sleep(randint(10, 20))
        total_posts = self.__get_number_of(
            "{}posts/".format(self.__format_userid(user)))
        # like all posts
        if count == 0:
            count = total_posts

        counter = 0
        err_counter = 0
        try:
            self.__open_first_userpost()

            while counter < count and counter < total_posts and err_counter < 5:
                try:
                    self.__click_like()
                    self._is_blocked()
                    # TODO: store the url for the liked post into table
                    time.sleep(randint(2, 4))
                    self.driver.find_element_by_xpath(
                        '/html/body').send_keys(Keys.RIGHT)
                    err_counter = 0
                except Exception as e:
                    err_counter += 1
                    logging.error(e, exc_info=True)
                    self.text_to_speech("Failed to like this post")
                time.sleep(randint(4, 10))
                counter += 1
            self.db_conn.execute('''UPDATE instaDB
                 SET posts_liked="{cnt}" where user_id="{usr}";'''.format(usr=user, cnt=counter))

        except Exception as e:
            logging.error(e, exc_info=True)
            self.text_to_speech("Like Userpost Failed")
        self.text_to_speech("Liked {} posts for user {}".format(counter, user))

    def _follow_user(self, user, hash_tag):
        """
        1. open user_profile
        2. click on follow
        """
        if self.driver.current_url != self.__format_userid(user):
            self.driver.get(self.__format_userid(user))
        try:
            self.__click_follow()
            self._is_blocked()
            self.db_conn.execute('''UPDATE instaDB
                 SET following=1, hash_tag="{tag}"
                 where user_id="{usr}";'''.format(usr=user, tag=hash_tag))
        except Exception as e:
            logging.error(e, exc_info=True)
            self.text_to_speech(
                "click_TO_FOLLOW error while following {}".format(user))

    def _insert_comment(self, comment):
        #  insert comment on user post
        try:
            self.__click_comment()
            self._is_blocked()
            _txt_box = self.driver.find_element_by_xpath(
                "//form/textarea[@aria-label='Add a comment…']")
            _txt_box.clear()
            # pyperclip.copy(comment)                 # copy
            # _txt_box.send_keys(Keys.CONTROL, 'v')   # paste
            self.driver.execute_script(
                'arguments[0].value = arguments[1]', _txt_box, comment)
            if len(comment) > 4:
                time.sleep(randint(4, 7))
            # signature to differentiate bot comment
            _txt_box.send_keys(' -ai ;)')
            _txt_box.send_keys(Keys.ENTER)
            time.sleep(randint(3, 7))
            self.text_to_speech("Commented {}".format(comment))
        except Exception as e:
            logging.error(e, exc_info=True)
            self.text_to_speech("Failed to insert comment")

    def _is_blocked(self):
        """
        1. check if the action is blocked
        2. exit program
        """
        time.sleep(randint(4, 8))
        blked = self.driver.find_elements_by_xpath(
            "//div/h3[contains(text(),'Action Blocked')]")
        if blked:
            self.driver.delete_all_cookies()
            logging.error("ERR: ACTION_BLOCKED")
            self.text_to_speech("Action has been blocked, closing program")
            self.__del__()
        else:
            pass

    # -------------------DM-REPORT------------------------
    def _group_users_list(self, group_name, group_code):
        self._open_group_chat(group_name, group_code)
        return self._get_group_users()

    def _sync_user_group(self, group_id, group_name, group_code):
        try:
            self.__reset_user_group_map()
            current_users = self._group_users_list(group_name, group_code)
            current_users.remove("Search")
            current_users.remove(self.user_id)
            for user in current_users:
                meta = self._user_meta(user)
                self._update_meta(user, meta)
                self.__map_user_group(user, group_id)
                try:
                    self.__open_first_userpost()
                    time.sleep(randint(2, 6))
                    try:
                        self.__click_like()
                    except:
                        logging.info("Post Already Liked")

                    post_url = self.driver.current_url
                    post_stamp = self.__get_post_timestamp()
                    self._sync_group_user_post(
                        user, group_id, post_url, post_stamp)
                except:
                    try:
                        current_users.remove(user)
                    except:
                        pass
        except Exception as e:
            logging.error(e, exc_info=True)
        self.db_conn.commit()

    def _check_mutual_likes(self, group_id, user_id, post_url, current_users):
        """
        open post-likes-list
        scroll through users - if users completed stop scrolling and update all_like as 1
        """
        try:
            self.driver.get(post_url)
            time.sleep(randint(2, 5))
            liked_list = self._get_likes_list()
            try:
                current_users.remove(user_id)
            except ValueError:
                print(f"user->{user_id} not in list")
            intersect = list(set(liked_list) & set(current_users))
            if set(intersect) == set(current_users):
                self.db_conn.execute(f'''UPDATE dim_group_user_post
                            SET liked_by_all=1 WHERE post_url="{post_url}"''')
            not_liked_by = list(set(current_users) - set(intersect))
            logging.info(
                f'''{post_url} not liked by {",".join(not_liked_by)}''')
            self._update_group_user_like(
                group_id, post_url, current_users, not_liked_by)
        except Exception as e:
            logging.info(
                f"Unable to get info for user {user_id} <-> post {post_url}")
            logging.error(e, exc_info=True)

    def _update_group_user_like(self, group_id, post_url, current_users, not_liked_by):
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
            ''', self.db_conn).empty:
                self.db_conn.execute(f'''INSERT INTO
                    fact_group_user_like(post_url,group_id ,user_id ,bool_like)
                    Values
                    ("{post_url}",{group_id},"{user_id}",{bool_like});
                ''')
            else:
                self.db_conn.execute(f'''UPDATE fact_group_user_like
                SET bool_like = {bool_like}
                WHERE
                    post_url="{post_url}"
                    AND group_id={group_id}
                    AND user_id="{user_id}";
                ''')
            logging.info(f"updated fact_group_user_like for {user_id}")
        self.db_conn.commit()
        #    df_group_user_like = pd.read_sql('select * from fact_group_user_like;', self.db_conn)

    def _get_likes_list(self):

        time.sleep(randint(3, 6))
        total_count = self.__likes_count()
        self.__click_expand_likes_btn()
        time.sleep(randint(3, 6))
        dialog = self.driver.find_element_by_xpath("//div/div[@role='dialog']")

        main_list = []
        li_cnt = 0
        prev_cnt = 0

        exit_counter = 0

        while(li_cnt < total_count and exit_counter <= 5):
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
            if li_cnt == prev_cnt or li_cnt >= 400:
                exit_counter += 1
                time.sleep(randint(3, 6))
            else:
                exit_counter = 0

        logging.info(f"total_likes:{total_count}<->list_count{li_cnt}")
        return main_list

    def _sync_group_user_post(self, user_id, group_id, post_url=None, timestamp=None):
        """
        user_id VARCHAR(30),
        group_id INT,
        post_url VARCHAR(80) NOT NULL,
        timestamp DATE,

        Enter only 1 post per day for a user_id,group_id
        """
        if (pd.read_sql(f'''
        select * from dim_group_user_post
        WHERE post_url="{post_url}"''', self.db_conn).empty) and (pd.read_sql(f'''
        select * from dim_group_user_post
        WHERE user_id="{user_id}"
        AND group_id={group_id}
        AND timestamp="{timestamp}"
        ''', self.db_conn).empty):
            self.db_conn.execute(f'''INSERT INTO
                        dim_group_user_post(user_id, group_id, post_url, timestamp) Values
                        ("{user_id}",{group_id},"{post_url}","{timestamp}");
                    ''')

    def _get_group_users(self):
        self.__click_group_info_icon()
        members = self.driver.find_elements_by_xpath("//div[@role='button']")
        usr_list = []
        for member in members:
            usr_id = member.find_element_by_tag_name(
                "div").text.splitlines()[0]
            usr_list.append(usr_id)
        return usr_list

    def _open_group_chat(self, group_name, group_code):
        self.driver.get(group_code)
        _href = group_code.split("instagram.com")[1]
        time.sleep(5)
        group_ele = self.driver.find_element_by_xpath(f"//a[@href='{_href}']")
        group_ele.click()
        time.sleep(randint(5, 10))

    def _send_chat(self, txt_msg):
        msg_box = self.driver.find_element_by_xpath(
            "//textarea[@placeholder='Message...']")
        msg_box.clear()
        for line in txt_msg.splitlines():
            msg_box.send_keys(line.strip())
            msg_box.send_keys(Keys.SHIFT, Keys.ENTER)
        time.sleep(randint(5, 10))
        msg_box.send_keys(Keys.ENTER)
        logging.info(txt_msg)


# --------------____________________________Private Func_________________________-------------------

    def __likes_count(self):
        #    why would I handle for 1 or 2 likes
        exp_btn = self.__get_expand_likes_btn()
        return int(exp_btn.text.replace(' others', ''))+1

    def __click_expand_likes_btn(self):
        #    return btn or false
        for btn in self.driver.find_elements_by_xpath("//button[@type='button']"):
            if ' others' in btn.text:
                btn.click()
                break
        else:
            raise NoSuchElementException

    def __get_expand_likes_btn(self):
        for btn in self.driver.find_elements_by_xpath("//button[@type='button']"):
            if ' others' in btn.text:
                return btn
        else:
            raise NoSuchElementException

    def __get_post_timestamp(self):
        timestamp = self.driver.find_element_by_tag_name(
            "time").get_attribute("title")
        return datetime.strptime(timestamp, "%b %d, %Y").date()

    def __map_user_group(self, user, group_id):
        self.db_conn.execute(f'''UPDATE instaDB SET group_id = {group_id}
        where user_id="{user}";''')

    def __reset_user_group_map(self):
        self.db_conn.execute(f'''UPDATE instaDB SET group_id = "{None}";''')

    def __click_group_info_icon(self):
        self.driver.execute_script(
            '''return document.querySelector('button>svg[aria-label="View Thread Details"]')
            .parentElement.click();''')

    # -------------------DM-REPORT------------------------
    def __predict(self, user_meta):
        # Add logic to calcute probability of user following you back
        # return Boolean
        try:
            if self.classifier_mod:
                _p = self.classifier_mod.predict(self.sc_X.transform(
                    [[user_meta['followers'], user_meta['following']]]))
                return bool(_p)
            else:
                # check if follower/following ratio is 90% or more
                # check if user has followers < 6000
                percent = user_meta['following']/user_meta['followers']*100
                return (percent > 90 and user_meta['followers'] < 6000)
        except ZeroDivisionError:
            return False
        except Exception as e:
            logging.error(e, exc_info=True)

    def _extract_hashtags(self):
        """
        TODO: test this out
        <a class=" xil3i" href="/explore/tags/puma/">#puma</a>
        return list of hashtags from a post
        """
        tags = self.driver.find_elements_by_xpath(
            "//span/a[contains(@href,'/explore/tags')]")
        return [tag.text for tag in tags]

    def __click_like(self):
        # click like button inside dialog box
        # use return to throw error when fails
        self.driver.execute_script(
            '''return document.querySelector('button>svg[aria-label="Like"]')
            .parentElement.click();''')

    def __click_comment(self):
        # click comment button inside dialog box
        self.driver.find_element_by_xpath(
            "//textarea[@aria-label='Add a comment…']").click()

    def __click_follow(self):
        # click follow btn
        self.driver.find_element_by_xpath(
            "//span/button[contains(text(),'Follow')]").click()

    def __get_tile_username(self):
        # return user_id from dialogbox
        dialog = self.driver.find_element_by_xpath("//div/div[@role='dialog']")
        return dialog.find_element_by_tag_name("h2").text

    def __open_first_userpost(self):
        # open first user post
        first_tile = self.driver.find_element_by_xpath("//article//a")
        first_tile.click()
        time.sleep(randint(4, 10))

    def __search_tag(self, tag_name):
        # search insta for tag
        self.driver.get(
            "https://www.instagram.com/explore/tags/{}/".format(tag_name.replace("#", "")))
        time.sleep(5)

    def __open_first_tile(self):
        # open first tile for tag_search
        if len(self.driver.find_elements_by_tag_name("h2")) == 2:
            # open first tile from MOST_RECENT
            first_tile = self.driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/article/div[2]/div/div[1]/div[1]/a')
            first_tile.click()
        else:
            # open first tile from TOP_POSTS when recents not available

            first_tile = self.driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a')
            first_tile.click()
        time.sleep(5)

    def __click_unfollow(self, u_name):
        # click unfollow and update in DB
        try:

            follow_btn = self.driver.find_element_by_xpath(
                "//button[contains(text(),'Following')]")
            follow_btn.click()

            unfollow_btn = self.driver.find_element_by_xpath(
                "//button[contains(text(),'Unfollow')]")
            unfollow_btn.click()
            self.text_to_speech("Unfollowed {}".format(u_name), False)
            time.sleep(randint(5, 20))
            self.db_conn.execute('''UPDATE instaDB
                 SET following=0 where user_id="{}";'''.format(u_name))
            self.db_conn.commit()
        except Exception as e:
            logging.error(e, exc_info=True)
            self.text_to_speech("ERR: while unfollowing {}".format(u_name))

    def __get_usr_name(self, usr_id):
        # return user_name from insta
        self.driver.get("https://www.instagram.com/{}/".format(usr_id))
        usr_name = self.driver.find_elements_by_tag_name('h1')[1].text
        self.db_conn.execute('''UPDATE creds SET user_name="{}"
             where user_id="{}"'''.format(usr_name, self.user_id))
        self.db_conn.commit()
        return usr_name

    def __get_number_of(self, btn_link):
        """
        TODO: re-write and reduce LOC
        """
        action = btn_link.split("/")[-2]
        if self.driver.current_url != btn_link.replace("{}/".format(action), ""):
            self.driver.get(btn_link.replace(
                "{}/".format(action), ""))
        try:
            count = self.driver.find_element_by_xpath(
                "//ul/li[substring-before(*,' {}')]".format(action)
            ).text.replace(action, "").strip().replace(",", "")
        except NoSuchElementException as e:
            action = action[:-1]
            count = self.driver.find_element_by_xpath(
                "//ul/li[substring-before(*,' {}')]".format(action)
            ).text.replace(action, "").strip().replace(",", "")
        except Exception as e:
            logging.error(e, exc_info=True)
            count = 0
        return self.__insta_number_conversion(count)

    def __get_list_of(self, attr_name="followers"):
        """
        1. get follower/following count
        2. open and iterate through the list
        3. return list
        """

        attr_count = self.__get_number_of(
            "https://www.instagram.com/{}/{}/".format(self.user_id, attr_name))
        self.text_to_speech("{} count is {}".format(attr_name, attr_count))

        attr_btn = self.driver.find_element_by_xpath(
            "//a[contains(@href,'/{}/{}/')]".format(self.user_id, attr_name))
        attr_btn.click()
        self.text_to_speech(
            "Scraping {} list, this operation will take time".format(attr_name), False)
        time.sleep(5)

        li_cnt = 0
        prev_cnt = 0
        ul_list = self.driver.find_elements_by_tag_name("ul")

        exit_counter = 0
        while(li_cnt <= attr_count and exit_counter <= 5):
            prev_cnt = li_cnt
            li_list = ul_list[-1].find_elements_by_tag_name("li")
            try:
                li_list[-1].location_once_scrolled_into_view
            except:
                li_list[-2].location_once_scrolled_into_view

            li_cnt = len(li_list)

            if li_cnt == prev_cnt:
                # self.text_to_speech(
                #     "Loading list, Current count is {} and will terminate in {}".format(li_cnt, exit_counter), False)
                exit_counter += 1
                time.sleep(randint(3, 6))
            else:
                exit_counter = 0

        self.text_to_speech(
            "Operation complete, formatting the results", False)

        _list = []
        for i in li_list:
            try:
                tmp_ele = i.find_element_by_tag_name("a")
                _list.append(self.__format_userid(
                    tmp_ele.get_attribute("href")))
            except Exception as e:
                logging.error(e, exc_info=True)
        self.text_to_speech("Returned {} values".format(len(_list)), False)
        return _list

    def __format_userid(self, link):
        # if link return username
        # if username return insta_url

        if len(link.split('/')) == 5:
            return link.split('/')[-2]
        else:
            return "https://www.instagram.com/{}/".format(link)

    def __insta_number_conversion(self, number):
        if type(number) != int:
            if "k" in number:
                return int(float(number.replace("k", ""))*1000)
            elif "m" in number:
                return int(float(number.replace("m", ""))*1000000)
            else:
                return int(number)
        else:
            return number

# --------------______________________________Utils______________________________-------------------

    def text_to_speech(self, text_string="Test", bool_print=True, bool_speak=True):
        # setup TTS for audio output
        if bool_print or self.headless:
            logging.info(text_string)
        if bool_speak and not self.bool_mute:
            self.engine.say(text_string)
            self.engine.runAndWait()
