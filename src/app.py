# -*- coding: utf-8 -*-

import asyncio
from aiohttp import web
import aiohttp_jinja2
import jinja2
import json
import motor.motor_asyncio
from datetime import datetime
import pytz


@aiohttp_jinja2.template('index.jinja2')
async def index(request):
    return {}


async def service(request):
    data = {
        'loaded': False,
    }

    id = request.query.get('id', None)
    hl = request.query.get('hl', 'en')
    if not hl in ['en', 'ru']:
        hl = 'en'

    if id is not None:
        doc = await get_params(id, hl)
        if doc:
            data = {
                'loaded': doc['parsed'],
                'perms': doc['perms'],
                'title': doc['title'],
                'company': doc['company'],
            }
        else:
            await insert(id, hl)

    return web.json_response(data)


async def get_params(id, hl):
    doc = collection.find_one({'id': id, 'hl': hl,})
    return await doc


async def insert(id, hl):
    insert_date = datetime.now(tz=pytz.timezone('UTC'))
    document = {
        'id': id,
        'hl': hl,
        'title': '',
        'company': '',
        'parsed': False,
        'date': insert_date,
        'perms': {},
    }
    await db.products.insert_one(document)


client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:gfhjkm@127.0.0.1:27017')
db = client.google
collection = db.products

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
app.add_routes([web.get('/', index),
                web.get('/service/', service),
                ])
app.router.add_static('/static', 'static', name='static')
app.router.add_static('/icons', '../icons', name='icons')

web.run_app(app)
