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
        self.compare_stats(self.follower_cnt, self.following_cnt, True)

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


# --------------____________________________Private Func_________________________-------------------

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


# --------------______________________________Utils______________________________-------------------


    def text_to_speech(self, text_string="Test", bool_print=True, bool_speak=True):
        # setup TTS for audio output
        if bool_print:
            print(text_string)
        if bool_speak:
            self.engine.say(text_string)
            self.engine.runAndWait()
