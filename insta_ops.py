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


class InstaOps:
    
    conn = sqlite3.connect('auto-insta.db')

    FOLLOWER_CNT = 0
    FOLLOWING_CNT = 0
    

    
    def __init__(self):
        
        options = webdriver.ChromeOptions() 
        options.add_argument(usr_profile)
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=options)
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice','HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')

