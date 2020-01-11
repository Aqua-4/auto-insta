#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 18:44:46 2019

@author: parashar
"""

from insta_ops import InstaOps
from random import randint, choice
import time
import multiprocessing as mp


def worker(user):
    instance = InstaOps(True, True, True, True)

    try:
        meta = instance._user_meta(user)
        instance._update_meta(user, meta, True)
    except:
        instance.db_conn.execute('''UPDATE instaDB
            SET acc_status=0 WHERE user_id="{usr}";
        '''.format(usr=user))


bot = InstaOps(False)
bot.account_init()

bot.sync_db()
bot.refresh_db()
bot.__del__()

incognito = InstaOps(True, True, True, True)
missing_users = incognito._get_missing_meta_users()

print("Commencing HAVOC, please close other applications...")
if __name__ == '__main__':
    p = mp.Pool(mp.cpu_count())
    p.map(worker, missing_users)


