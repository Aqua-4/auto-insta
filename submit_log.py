#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 18:18:24 2019

@author: parashar
"""

import sqlite3
import pandas as pd
import shutil


db_conn = sqlite3.connect('auto-insta.db')

usr = pd.read_sql("select user_id from creds",con=db_conn).user_id[0]
db_copy = '{}_db.db'.format(usr)
shutil.copy('auto-insta.db',db_copy)

db_conn = sqlite3.connect(db_copy)
db_conn.execute("DROP TABLE creds")
print("Successfully removed all the Login detials")
db_conn.commit()

print("File *auto_insta.log* and *{}* can now be sent to the dev".format(db_copy))