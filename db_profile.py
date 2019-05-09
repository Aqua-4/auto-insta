"""
Update/Insert user_meta into db
for Machine-Learning
"""

from insta_ops import InstaOps
import pandas as pd

x = InstaOps()
x.account_init()
x.sync_db()


def update_meta(user, user_meta):
    foc = user_meta['followers']
    fic = user_meta['following']
    posts = user_meta['posts']
    if pd.read_sql('select * from instaDB where user_id="{}"'.format(user), x.db_conn).empty:
        x.db_conn.execute('''INSERT INTO
            instaDB(user_id,followers_cnt,following_cnt,posts,acc_status) Values
            ("{usr}",{followers},{following},{posts},1);
        '''.format(usr=user, followers=foc, following=fic, posts=posts))
    else:
        x.db_conn.execute('''UPDATE instaDB
            SET following_cnt={following}, followers_cnt={followers},
            posts={posts}, acc_status=1 WHERE user_id="{usr}";
        '''.format(usr=user, followers=foc, following=fic, posts=posts))
    x.db_conn.commit()


users = pd.read_sql("""select user_id from instaDB where
         followers_cnt IS NULL;""", x.db_conn).user_id
for user in users:
    try:
        meta = x._user_meta(user)
        update_meta(user, meta)
    except:
        x.text_to_speech("User {} has been removed by insta".format(user))
        x.db_conn.execute('''UPDATE instaDB
            SET acc_status=0 WHERE user_id="{usr}";
        '''.format(usr=user))
