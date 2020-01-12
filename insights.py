# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 21:19:23 2020

@author: Parashar
"""


import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

db_conn = sqlite3.connect('auto-insta.db')
db_df = pd.read_sql("select * from instaDb", db_conn)
bot_df =pd.read_sql("select * from instaDb where bot_lead=1", db_conn)
bot_foll_df =pd.read_sql("select * from instaDb where bot_lead=1 AND following=1 AND acc_status=1", db_conn)
bot_fb_df=pd.read_sql("select * from instaDb where bot_lead=1  AND followers=1", db_conn)

hash_df = bot_foll_df.groupby(['hash_tag'],as_index=False).sum()
hash_df.sort_values("followers",ascending=False,inplace=True)
#bot_foll_df.plot(kind='bar',x='hash_tag',y='followers',color='red')
hash_df.plot(title="Most Followed hashtags", kind='bar',x='hash_tag',y='followers',color='red')
plt.show()
hash_df.to_csv("most_followed_hastags.csv",index=False)

bot_fb_df.plot(kind='scatter',x='following_cnt',y='followers_cnt',color='green')
plt.show()
bot_fb_df.to_csv("follow_back_users.csv",index=False)


