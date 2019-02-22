# -*- coding: utf-8 -*-

import asyncio, random, time
import motor.motor_asyncio
from datetime import datetime
import pytz
import requests
import re
import json
import os
import hashlib


async def rnd_sleep(t):
    await asyncio.sleep(t * random.random() * 2)


async def producer(queue, collection):
    while True:
        cursor = collection.find({'parsed': False})
        async for doc in cursor:
            await queue.put(doc)


async def consumer(queue, collection):
    while True:
        doc = await queue.get()

        perms = parse(doc['id'], doc['hl'])

        await collection.update_one({'_id': doc['_id']}, {'$set': {
            'parsed': True,
            'perms': perms,
            'date': datetime.now(tz=pytz.timezone('UTC')),
        }})

        print('updated')

        queue.task_done()


def parse(id, hl):
    print('parsing: %s, %s' % (id, hl))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://play.google.com/',
        'X-Same-Domain': '1',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Connection': 'keep-alive',
        'TE': 'Trailers',
    }

    params = {
        'rpcids': 'xdSrCf',
        'hl': hl,
        'authuser': '',
        'soc-app': '121',
        'soc-platform': '1',
        'soc-device': '1',
        'rt': 'c',
    }

    data = {
        'f.req': '[[["xdSrCf","[[null,[\\"%s\\",7],[]]]",null,"vm96le:0|iA"]]]' % id,
        '': ''
    }

    response = requests.post('https://play.google.com/_/PlayStoreUi/data/batchexecute', headers=headers, params=params,
                             data=data)

    text = re.sub(r'^.*?\[', '[', response.text, flags=re.S)
    text = re.sub(r',,', ',null,', text, flags=re.M | re.S)
    text = re.sub(r',,', ',null,', text, flags=re.M | re.S)
    text = re.sub(r'\[,', '[null,', text, flags=re.M | re.S)

    text = re.sub(r'\]\s+\]\s+\d+\s+\[\[', "]],[[", text, flags=re.M | re.S)
    text = '[' + text + ']'

    data = json.loads(text)[0][0][2]
    data = json.loads(data)[0]

    perms = []

    for item in data:
        title = item[0]
        icon = item[1][3][2]
        perm_list = item[2]
        permissions = []
        for p in perm_list:
            if isinstance(p, list):
                permissions.append(p[1])

        m = hashlib.md5()
        m.update(icon.encode())
        icon_name = m.hexdigest() + '.png'

        icon_path = '../icons/' + icon_name
        if not os.path.exists(icon_path):
            r = requests.get(icon)
            with open(icon_path, 'wb') as f:
                f.write(r.content)

        perms.append({
            'title': title,
            'icon': icon_name,
            'perms': permissions,
        })

    return perms


async def main():
    queue = asyncio.Queue()

    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:gfhjkm@127.0.0.1:27017')
    db = client.google
    collection = db.products

    # fire up the both producers and consumers
    producers = [asyncio.ensure_future(producer(queue, collection))
                 for _ in range(1)]
    consumers = [asyncio.ensure_future(consumer(queue, collection))
                 for _ in range(1)]

    await asyncio.gather(*producers)
    await queue.join()

    for c in consumers:
        c.cancel()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
