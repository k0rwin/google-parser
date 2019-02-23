# -*- coding: utf-8 -*-

import motor.motor_asyncio
from datetime import datetime
import pytz


# client = motor.motor_asyncio.AsyncIOMotorClient()

# mongodb://myDBReader:D1fficultP%40ssw0rd@mongodb0.example.com:27017/admin
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:gfhjkm@127.0.0.1:27017')

db = client.google

async def do_insert():
    insert_date = datetime.now(tz=pytz.timezone('UTC'))
    document = {
        'id': 'com.amazon.mShop.android.shopping',
        # 'id': 'org.telegram.messenger',
        # 'id': 'jp.co.yahoo.android.yjtop',
        # 'id': 'com.twitter.android',
        'hl': 'en',
        'title': '',
        'company': '',
        'parsed': False,
        'date': insert_date,
        'perms': {},
    }
    result = await db.products.insert_one(document)
    print('result %s' % repr(result.inserted_id))


import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(do_insert())
