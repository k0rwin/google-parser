# -*- coding: utf-8 -*-

import asyncio
from aiohttp import web
import aiohttp_jinja2
import jinja2
import json
import motor.motor_asyncio
from datetime import datetime
import pytz
import os


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


print('-------------------------------------------')
print('Starting App')
print('-------------------------------------------')

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://%s:%s@%s:%s' % (
os.environ['MONGO_USER'], os.environ['MONGO_PASS'], os.environ['MONGO_HOST'], os.environ['MONGO_PORT']))
db = client.google
collection = db.products

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(APP_DIR, 'src', 'templates')))
app.add_routes([web.get('/', index),
                web.get('/service/', service),
                ])

app.router.add_static('/static', os.path.join(APP_DIR, 'src', 'static'), name='static')
app.router.add_static('/icons', os.path.join(APP_DIR, 'icons'), name='icons')

web.run_app(app)
