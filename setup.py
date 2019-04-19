"""
1. use touch auto-insta.db
2. create DB schema using sqlite3 module
"""
import sqlite3

conn = sqlite3.connect('auto-insta.db')

conn.execute('''CREATE TABLE instaDB
         (user_id VARCHAR(30) PRIMARY KEY NOT NULL,
         follower INT,
         following INT,
         acc_status INT DEFAULT 1,
         bot_lead INT DEFAULT 0,
         timestamp DATE
         )
         WITHOUT ROWID;''')

print("App setup complete")
