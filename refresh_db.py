#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 18:44:46 2019

@author: parashar
"""

from insta_ops import InstaOps


bot = InstaOps(False)
bot.account_init()

bot.sync_db()
bot.refresh_db()
bot.__del__()

incognito = InstaOps(False, True, True)
incognito.refresh_db()
