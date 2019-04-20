"""
1. use touch auto-insta.db
2. create DB schema using sqlite3 module
"""
import sqlite3

conn = sqlite3.connect('auto-insta.db')

conn.execute('''CREATE TABLE instaDB
         (user_id VARCHAR(30) PRIMARY KEY NOT NULL,
         followers INT DEFAULT 0,
         following INT DEFAULT 0,
         acc_status INT DEFAULT 1,
         bot_lead INT DEFAULT 0,
         timestamp DATE
         )
         WITHOUT ROWID;''')

conn.execute('''CREATE TABLE creds
         (user_id VARCHAR(30) PRIMARY KEY NOT NULL,
         user_name VARCHAR(30),
         passwd VARCHAR(128),
         chromedata VARCHAR(128)
         )
         WITHOUT ROWID;''')

conn.commit()

print("App setup complete")
