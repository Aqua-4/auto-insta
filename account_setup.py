import sqlite3
from getpass import getpass

conn = sqlite3.connect('auto-insta.db')

user_id = input("User ID/Email:")
passwd = getpass("Insert Password:")

conn.execute("DELETE from creds")

conn.execute('''INSERT INTO creds (user_id,passwd)
         VALUES("{}","{}")
        '''.format(user_id, passwd))


print("credentials have been udpated")
print('Do you want to update "Chrome Data Location"')
if input("press y or n:-").lower() == 'y':
    path_loc = input("Path Location:")
    conn.execute('UPDATE creds SET chromedata="{}" where user_id="{}"'.format(
        path_loc.replace("/", "//"), user_id))
    print("Chrome Location has been Updated")


conn.commit()
