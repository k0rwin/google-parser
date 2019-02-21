# -*- coding: utf-8 -*-

import asyncio, random, time
import motor.motor_asyncio
from datetime import datetime
import pytz

async def rnd_sleep(t):
    await asyncio.sleep(t * random.random() * 2)

async def producer(queue, collection):
    while True:
        cursor = collection.find({'parsed': False})
        async for doc in cursor:
            print(doc)
            await queue.put(doc)
            await rnd_sleep(2)

async def consumer(queue, collection):
    while True:
        doc = await queue.get()
        print('consumed %s' % doc)

        # parsing

        await collection.update_one({'_id': doc['_id']}, {'$set': {
            'parsed': True
        }})

        print('updated')

        queue.task_done()

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
