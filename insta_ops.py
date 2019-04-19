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
    USR_ID = pd.read_sql("select user_id from creds",conn).user_id[0]


    def __init__(self): 
        options = webdriver.ChromeOptions()  
        chromedata = pd.read_sql("select chromedata from creds",conn).chromedata[0]
        if chromedata:
            options.add_argument(chromedata)
        options.add_argument("--start-maximized") 
        self.driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=options)
        self.engine = pyttsx3.init()
        
