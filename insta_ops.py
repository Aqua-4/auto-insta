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
        self.db_conn = sqlite3.connect('auto-insta.db')
        self.user_id = pd.read_sql(
            "select user_id from creds", self.db_conn).user_id[0]

        options = webdriver.ChromeOptions()
        chromedata = pd.read_sql(
            "select chromedata from creds", self.db_conn).chromedata[0]
        if chromedata:
            options.add_argument(chromedata)
        options.add_argument("--start-maximized")

        exec_path = "chromedriver"
        if platform.system() == 'Linux':
            exec_path = "./chromedriver"

        self.driver = webdriver.Chrome(
            executable_path=exec_path, chrome_options=options)
        self.engine = pyttsx3.init()

    def insta_login(self):

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

        self.user_name = self.__get_usr_name()
        login_greet = "Welcome {}, you have been logged into your account and ".format(
            self.user_name)
        login_greet += "here are your stats for the current session "
        self.text_to_speech(login_greet, False)
        self.FOLLOWER_CNT = self.get_number_of(
            "https://www.instagram.com/{}/followers/".format(self.user_id))
        self.FOLLOWING_CNT = self.get_number_of(
            "https://www.instagram.com/{}/following/".format(self.user_id))
        self.compare_stats(self.FOLLOWER_CNT, self.FOLLOWING_CNT, True)

# --------------____________________________Private Func_________________________-------------------

    def __get_usr_name(self):
        # update/get user_name from insta/db

        self.driver.get("https://www.instagram.com/{}/".format(self.user_id))
        usr_name = pd.read_sql(
            "select user_name from creds", self.db_conn).user_name[0]
        if usr_name:
            return usr_name
        else:
            usr_name = self.driver.find_elements_by_tag_name('h1')[1].text
            self.db_conn.execute('''UPDATE creds SET user_name="{}"
             where user_id="{}"'''.format(usr_name, self.user_id))
            return usr_name


# --------------______________________________Utils______________________________-------------------

    def text_to_speech(self, text_string="Test", bool_print=True, bool_speak=True):
        # setup TTS for audio output
        if bool_print:
            print(text_string)
        if bool_speak:
            self.engine.say(text_string)
            self.engine.runAndWait()
