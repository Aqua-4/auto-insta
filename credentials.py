import sqlite3
from getpass import getpass

conn = sqlite3.connect('auto-insta.db')

user_id = input("User ID/Email:")
passwd = getpass("Insert Password:")

conn.execute("DELETE from creds")

conn.execute('''INSERT INTO `creds` (user_id,passwd)
         VALUES("{}","{}")
        '''.format(user_id, passwd))

conn.commit()

print("credentials have been udpated")
