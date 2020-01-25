"""
Check if the bot is able to login into user account
"""

from insta_ops import InstaOps
import multiprocessing as mp
import pandas as pd

def worker(hash_tag):
    instance = InstaOps(True, True, True, True)
    if instance._bool_check_tag(hash_tag):
        return hash_tag

tags_df = pd.read_excel('insta_config.xlsx', sheet_name='hashtags')
tags = list(tags_df.hashtags)

print("Checking for working hash_tags from insta_config")
print("Commencing HAVOC, please close other applications...")
if __name__ == '__main__':
    p = mp.Pool(mp.cpu_count())
    working_hashtags=(p.map(worker, tags))
    _ = pd.DataFrame(working_hashtags, columns=["hashtags"])
    _.to_csv("working_hashtags.csv",index=False)
    print('Created "working_hashtags.csv"')


print("Checking user login")
bot = InstaOps(False)
bot.account_init()
