# -*- coding: utf-8 -*-

import asyncio
import motor.motor_asyncio
from datetime import datetime, timedelta
import pytz
import requests
import re
import json
import os
import hashlib


async def producer(queue, collection):
    while True:
        expired = datetime.now(tz=pytz.timezone('UTC')) - timedelta(days=int(os.environ['REPARSE_EVERY_DAYS']))

        cursor = collection.find({
            '$or': [
                {
                    'parsed': False,
                },
                {
                    'date': {
                        '$lt': expired,
                    },
                },
            ],
        }).limit(int(os.environ['DB_READ_COUNT']))
        async for doc in cursor:
            await queue.put(doc)

        await asyncio.sleep(int(os.environ['DB_READ_DELAY']))


async def consumer(queue, collection):
    while True:
        doc = await queue.get()
        print('consumed: %s' % doc['id'])
        data = parse(doc['id'], doc['hl'])

        await collection.update_one({'_id': doc['_id']}, {'$set': {
            'parsed': True,
            'title': data['title'],
            'company': data['company'],
            'perms': data['perms'],
            'date': datetime.now(tz=pytz.timezone('UTC')),
        }})

        queue.task_done()


def parse(id, hl):
    print('Parse: %s' % id)
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
        'id': id,
        'hl': hl,
    }

    response = requests.get('https://play.google.com/store/apps/details', headers=headers, params=params)

    matches = re.search(r'<meta itemprop="name" content="(.*?)\"', response.text, flags=re.M | re.S)
    product_title = ''
    if matches:
        product_title = matches.group(1)
    print('product_title: %s' % product_title)

    matches = re.search(r'<a.*?href="https://play.google.com/store/apps/developer\?id=.*?".*?>(.*?)</a>', response.text,
                        flags=re.M | re.S)
    company = ''
    if matches:
        company = matches.group(1)

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

    print(data)

    for item in data:
        if len(item):
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

    return {
        'title': product_title,
        'company': company,
        'perms': perms,
    }


async def main():
    print('-------------------------------------------')
    print('Starting parser')
    print('-------------------------------------------')
    queue = asyncio.Queue()

    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://%s:%s@%s:%s' % (
        os.environ['MONGO_USER'], os.environ['MONGO_PASS'], os.environ['MONGO_HOST'], os.environ['MONGO_PORT']))
    db = client.google
    collection = db.products

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
