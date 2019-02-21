# -*- coding: utf-8 -*-

import motor.motor_asyncio
from datetime import datetime
import pytz


# client = motor.motor_asyncio.AsyncIOMotorClient()

# mongodb://myDBReader:D1fficultP%40ssw0rd@mongodb0.example.com:27017/admin
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:gfhjkm@127.0.0.1:27017')

db = client.google

async def do_insert():
    # document = {'id': 'org.telegram.messenger', 'hl': 'en', }
    # document = {'id': 'jp.co.yahoo.android.yjtop', 'hl': 'en', }
    # document = {'id': 'com.twitter.android', 'hl': 'en', }
    insert_date = datetime.now(tz=pytz.timezone('UTC'))
    document = {
        'id': 'com.amazon.mShop.android.shopping',
        'hl': 'en',
        'parsed': False,
        'date': insert_date
    }
    result = await db.products.insert_one(document)
    print('result %s' % repr(result.inserted_id))


import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(do_insert())
