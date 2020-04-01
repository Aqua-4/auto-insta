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
         timestamp DATE,
         group_id INT
         )
         WITHOUT ROWID;''')

# conn.execute("ALTER TABLE instaDB ADD group_id INT;")

# maybe create a table for keeping a track of liked_user_posts with column as url
conn.execute('''CREATE TABLE smartlog
         (session_start VARCHAR(26) PRIMARY KEY NOT NULL,
         session_end VARCHAR(26),
         followers_cnt INT,
         following_cnt INT,
         delta_followers_cnt INT,
         delta_following_cnt INT
         )
         WITHOUT ROWID;''')

conn.execute('''CREATE TABLE creds
         (user_id VARCHAR(30) PRIMARY KEY NOT NULL,
         user_name VARCHAR(30),
         passwd VARCHAR(128),
         chromedata VARCHAR(128)
         )
         WITHOUT ROWID;''')

# group_id is auto-increment
conn.execute('''CREATE TABLE dim_group
         (group_id INTEGER PRIMARY KEY,
         group_name VARCHAR(40),
         group_rules TEXT,
         group_code VARCHAR(80)
         ); ''')

conn.execute('''CREATE TABLE dim_group_user_post
         (post_id INTEGER PRIMARY KEY,
         group_id INT,
         user_id VARCHAR(30),
         post VARCHAR(80) NOT NULL,
         timestamp DATE,
         liked_by_all INT DEFAULT 0
         );''')

conn.execute('''CREATE TABLE fact_group_user_like
         (post_id INT,
         group_id INT,
         user_id VARCHAR(30),
         bool_like INT DEFAULT 0
         );''')

conn.commit()

print("App setup complete")
