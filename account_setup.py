import sqlite3
from getpass import getpass

conn = sqlite3.connect('auto-insta.db')

print("Do not insert email for login, please use user_id")
user_id = input("Insert user_id:")
passwd = getpass("Insert Password:")

conn.execute("DELETE from creds")

conn.execute('''INSERT INTO creds (user_id,passwd)
         VALUES("{}","{}")
        '''.format(user_id, passwd))


print("credentials have been udpated")
print('Do you want to update "Chrome Data Location"')

how_to = """
*****How to Find Path Location:*******
1. Open chrome
2. open Link/URL "chrome://version/"
3. copy "Profile Path"
4. paste here
"""

if input("press y or n:-").lower() == 'y':
    print(how_to)
    path_loc = input("Path Location:")
    conn.execute('UPDATE creds SET chromedata="{}" where user_id="{}"'.format(
        path_loc.replace("/", "//"), user_id))
    print("Chrome Location has been Updated")


conn.commit()
