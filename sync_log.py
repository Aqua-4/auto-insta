#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 16:10:59 2019

@author: parashar
"""
import sqlite3
import pandas as pd


db_conn = sqlite3.connect('auto-insta.db')

with open("auto_insta.log") as f:
    f = f.readlines()

master_dict = {'user': [], 'likes': [], 'hashtag': []}
hashtag = ""
for line in f:
    if 'searching for tag' in line:
        hashtag = "#{}".format(line.split("#")[1].strip())
#        if hashtag not in master_dict:
#            master_dict[hashtag] =[]
    elif '[INFO] Liked ' in line:
        user = line.split("user")[-1].strip()
        likes = line.split('[INFO] Liked ')[-1].split('posts')[0]
        master_dict['user'].append(user)
        master_dict['likes'].append(likes)
        master_dict['hashtag'].append(hashtag)
        db_conn.execute("""
        UPDATE instaDB SET
        hash_tag="{tag}", posts_liked={likes}, bot_lead=1
        WHERE user_id="{user}"
        """.format(user=user, likes=likes, tag=hashtag))

db_conn.commit()
df = pd.DataFrame.from_dict(master_dict)
