"""
1. use touch auto-insta.db
2. create DB schema using sqlite3 module
"""
import sqlite3

conn = sqlite3.connect('auto-insta.db')

# 304 is the char limit for hashtag
conn.execute('''CREATE TABLE instaDB
         (user_id VARCHAR(30) PRIMARY KEY NOT NULL,
         followers INT DEFAULT 0,
         following INT DEFAULT 0,
         posts INT,
         followers_cnt INT,
         following_cnt INT,
         acc_status INT DEFAULT 1,
         bot_lead INT DEFAULT 0,
         hash_tag VARCHAR(64),
         posts_liked INT,
         timestamp DATE
         )
         WITHOUT ROWID;''')

# maybe create a table for keeping a track of liked_user_posts with column as url

conn.execute('''CREATE TABLE creds
         (user_id VARCHAR(30) PRIMARY KEY NOT NULL,
         user_name VARCHAR(30),
         passwd VARCHAR(128),
         chromedata VARCHAR(128)
         )
         WITHOUT ROWID;''')

conn.commit()

print("App setup complete")
