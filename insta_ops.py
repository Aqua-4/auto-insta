# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 01:47:07 2018

@author: Parashar
-----------------------------------------------------------------------
All Instagram Operations
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import datetime
import random
import sqlite3
import time
import pyttsx3
import platform


class InstaOps:

    def __init__(self):
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
        # options.add_argument("--headless")

        if chromedata:
            options.add_argument('user-data-dir={}'.format(chromedata))

        exec_path = "chromedriver"
        if platform.system() == 'Linux':
            exec_path = "./chromedriver"

        self.driver = webdriver.Chrome(
            executable_path=exec_path, chrome_options=options)
        self.engine = pyttsx3.init()
        self.text_to_speech("Insta Bot has been initialized")

    def __del__(self):
        self.db_conn.commit()
        self.db_conn.close()
        self.text_to_speech("Shutting Down Instagram Bot", False)
        self.driver.quit()
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
        self._sync_db_col("followers")
        self._sync_db_col("following")

    def smart_activity(self, user_count=6, per_user_like=4):
        """
        1. navigate to random hashtag from list __search_tag("#tag")
        2. open "recently posted first tile"
        3. navigate through posts collecting user_names
        4. follow and like  if bot predicts that user will followback
        """
        # get 3 times the user_name incase of worst case scenario
        users = self._extract_users_from_tile(user_count*3)
        for user in users:
            try:
                user_meta = self._user_meta(user)
                self._update_meta(user, user_meta)
                if self.__predict(user_meta):
                    self._follow_user(user)
                    self._like_userpost(user, per_user_like)
                else:
                    self.text_to_speech(
                        "Algorithm predicts that user {} won't follow back".format(user), False)
            except:
                print("xxxxxxxx-------Edge case occurred------xxxxxxxx",
                      self.driver.current_url)
                self.account_init()

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
        self.__search_tag(tag_name)
        try:
            self.__open_first_tile()
        except:
            self.text_to_speech(
                "Tag search and open failed for {}".format(tag_name))


# --------------_______________________SEMI-Private Func_________________________-------------------


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

    def _sync_db_col(self, column="followers"):
        # sync db column - followers/following

        col_list = self.__get_list_of(column)

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
        self.text_to_speech("Column {} has been synced with DB".format(column))

    def _unfollow_user(self, u_name):
        # goto user_profile and unfollow
        insta_link = self.__format_userid(u_name)
        self.driver.get(insta_link)
        time.sleep(random.randint(5, 10))
        if len(self.driver.find_elements_by_tag_name("h2")):
            self.db_conn.execute('''UPDATE instaDB SET acc_status=0
             where user_id="{}"'''.format(u_name))
            self.text_to_speech(
                "User {} acc does not exist anymore".format(u_name), False)
        else:
            self.__click_unfollow(u_name)

    def _extract_users_from_tile(self, user_count=20):
        # return list of usernames
        _list = []
        while len(_list) < user_count:
            try:
                _list.append(self.__get_tile_username())
            except:
                self.text_to_speech("Cannot get user_name")
            click_right = self.driver.find_element_by_xpath('/html/body')
            click_right.send_keys(Keys.RIGHT)
            # unique list of user_names
            _list = list(set(_list))
            time.sleep(random.randint(4, 10))
        return _list

    def _update_meta(self, user, user_meta):
        foc = user_meta['followers']
        fic = user_meta['following']
        posts = user_meta['posts']
        if pd.read_sql('select * from instaDB where user_id="{}"'.format(user), self.db_conn).empty:
            self.db_conn.execute('''INSERT INTO
             instaDB(user_id,followers_cnt,following_cnt,posts,acc_status,bot_lead) Values
             ("{usr}",{followers},{following},{posts},1,1);
            '''.format(usr=user, followers=foc, following=fic, posts=posts))
        else:
            self.db_conn.execute('''UPDATE instaDB
             SET following_cnt={following}, followers_cnt={followers},
             posts={posts}, acc_status=1, bot_lead=1 WHERE user_id="{usr}";
            '''.format(usr=user, followers=foc, following=fic, posts=posts))
        self.db_conn.commit()

    def _user_meta(self, u_name):
        meta = {}
        user_url = self.__format_userid(u_name)
        meta['followers'] = self.__get_number_of(
            "{}followers/".format(user_url))
        meta['following'] = self.__get_number_of(
            "{}following/".format(user_url))
        meta['posts'] = self.__get_posts_count()
        return meta

    def _like_userpost(self, user, count=0):
        """
        1. Navigate to user profile
        2. Like n number of posts
        """
        if self.driver.current_url != self.__format_userid(user):
            self.driver.get(self.__format_userid(user))
        time.sleep(random.randint(10, 20))
        total_posts = self.__get_posts_count()
        if count == 0:
            count = total_posts

        try:
            self.__open_first_userpost()

            err_counter = 0
            counter = 0
            while counter < count and counter < total_posts and err_counter < 5:
                try:
                    self.__click_like()
                    time.sleep(random.randint(2, 4))
                    self.driver.find_element_by_xpath(
                        '/html/body').send_keys(Keys.RIGHT)
                    err_counter = 0
                except:
                    err_counter += 1
                    self.text_to_speech("Failed to like this post")
                time.sleep(random.randint(4, 10))
                counter += 1

        except:
            self.text_to_speech("Like Userpost Failed")
        self.text_to_speech("Liked {} posts for user {}".format(counter, user))

    def _follow_user(self, user):
        """
        1. open user_profile
        2. click on follow
        """
        if self.driver.current_url != self.__format_userid(user):
            self.driver.get(self.__format_userid(user))
        try:
            self.__click_follow()
            self.db_conn.execute('''UPDATE instaDB
                 SET following=1 where user_id="{}";'''.format(user))
        except:
            self.text_to_speech(
                "click_TO_FOLLOW error while following {}".format(user))
# --------------____________________________Private Func_________________________-------------------

    def __predict(self, user_meta):
        # Add logic to calcute probability of user following you back
        # return Boolean
        try:
            percent = user_meta['following']/user_meta['followers']*100
            return (percent > 55)
        except:
            return False

    def __click_like(self):
        # click like button inside dialog box
        dialog = self.driver.find_element_by_xpath("//div/div[@role='dialog']")
        dialog.find_element_by_xpath(
            "//span[@aria-label='Like']").click()

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
        first_tile = self.driver.find_element_by_tag_name("article")
        first_tile.find_element_by_tag_name("a").click()
        time.sleep(random.randint(4, 10))

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
            time.sleep(random.randint(5, 20))
            self.db_conn.execute('''UPDATE instaDB
                 SET following=0 where user_id="{}";'''.format(u_name))
            self.db_conn.commit()
        except:
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
        # return number of followers/following
        if self.driver.current_url != btn_link.replace("{}/".format(btn_link.split("/")[-2]), ""):
            self.driver.get(btn_link.replace(
                "{}/".format(btn_link.split("/")[-2]), ""))
        btn_href = btn_link
        links = self.driver.find_elements_by_tag_name("a")
        try:
            _count = [
                href for href in links if btn_href in href.get_attribute("href")][0].text
            count = _count.split(' ')[0].replace(",", "")
        except:
            count = 0
        return self.__insta_number_conversion(count)

    def __get_posts_count(self):
        # return total posts by user
        count = self.driver.find_element_by_xpath(
            '//li/span/span').text.replace(",", "")
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
                time.sleep(random.randint(3, 6))
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
            except:
                print("ERR: ")
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
        if bool_print:
            print(text_string)
        if bool_speak:
            self.engine.say(text_string)
            self.engine.runAndWait()
