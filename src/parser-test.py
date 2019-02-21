# -*- coding: utf-8 -*-

import requests
import json

params = {
    'id': 'jp.co.yahoo.android.yjtop',
    'hl': 'en',
}

headers = {}

body = {
    'f.req': '[[["xdSrCf","[[null,["jp.co.yahoo.android.yjtop",7],[]]]",null,"vm96le:0|Nz"]]]',
    'at': 'AK6RGVYJeuvs7NND46ZHn6m90ai7:1550741541704',
}


# r = requests.get('https://play.google.com/store/apps/details', headers=headers, params=params)

r = requests.post('https://play.google.com/_/PlayStoreUi/data/batchexecute?hl=en&authuser=0&soc-app=121&soc-platform=1&soc-device=1&rt=c', headers=headers, json=body)

print(r.text)
