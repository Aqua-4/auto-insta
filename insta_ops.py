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
        if chromedata:
            options.add_argument('user-data-dir={}'.format(chromedata))

        exec_path = "chromedriver"
        if platform.system() == 'Linux':
            exec_path = "./chromedriver"

        self.driver = webdriver.Chrome(
            executable_path=exec_path, chrome_options=options)
        self.engine = pyttsx3.init()

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

    def smart_like(self, user_count=2, per_user_like=3):
        """
        1. navigate to random hashtag from list
        2. open "recently posted first tile"
        3. navigate through posts collecting user_names
        4. smart_like(username)
        """
        users = []
        while len(users) < user_count:
            try:
                user_name = self.driver.find_element_by_xpath(
                    '/html/body/div[3]/div/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a')
                users.append(user_name.text)
            except:
                print("unable to load")
            click_right = self.driver.find_element_by_xpath('/html/body')
            click_right.send_keys(Keys.RIGHT)
            users = list(set(users))
            time.sleep(random.randint(4, 10))
        for user in users:
            liked_url = []

            self.driver.get("https://www.instagram.com/{}/".format(user))

            time.sleep(random.randint(10, 20))

            # open first tile
            try:
                first_tile = self.driver.find_element_by_tag_name("article")
                first_tile.find_element_by_tag_name("a").click()
            except:
                print("ERR: No First Tile")

            time.sleep(random.randint(4, 10))
            err_counter = 0
            counter = 0
            while counter < per_user_like and err_counter < 5:
                try:
                    like_btn = self.driver.find_element_by_tag_name("section")
                    like_btn.find_element_by_xpath(
                        "//span[@aria-label='Like']").click()
                    err_counter = 0
                except:
                    err_counter += 1
                    print("ERR: failed to like")
                try:
                    self.driver.find_element_by_xpath(
                        '/html/body').send_keys(Keys.RIGHT)
                    time.sleep(random.randint(4, 10))
                except:
                    err_counter += 1
                    print("ERR: unable to load next post")
                time.sleep(random.randint(4, 10))
                liked_url.append(self.driver.current_url)
                counter += 1

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

    def tagsearch_n_open(self, tag_name):
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
            self.db_conn.commit()


# --------------____________________________Private Func_________________________-------------------


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

        except:
            self.text_to_speech("ERR: while unfollowing {}".format(u_name))

    def __get_usr_name(self, usr_id):
        # return user_name from insta

        self.driver.get("https://www.instagram.com/{}/".format(usr_id))
        usr_name = self.driver.find_elements_by_tag_name('h1')[1].text
        self.db_conn.execute('''UPDATE creds SET user_name="{}"
             where user_id="{}"'''.format(usr_name, self.user_id))
        return usr_name

    def __get_number_of(self, btn_link):
        # return number of followers/following

        self.driver.get(btn_link)
        btn_href = btn_link
        links = self.driver.find_elements_by_tag_name("a")
        post_count = [
            href for href in links if btn_href in href.get_attribute("href")][0].text
        # need to handle for 1k,1M and further
        int_count = int(post_count.split(' ')[0].replace(",", ""))
        return int_count

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

# --------------______________________________Utils______________________________-------------------

    def text_to_speech(self, text_string="Test", bool_print=True, bool_speak=True):
        # setup TTS for audio output
        if bool_print:
            print(text_string)
        if bool_speak:
            self.engine.say(text_string)
            self.engine.runAndWait()
