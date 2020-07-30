# coding: utf-8
import requests
import json
import base64
import os
import random
import uuid
import multiprocessing
import traceback
def search(q, url):
    try:
            data = {
                'question': q
            }
            response = requests.post(url, data)
            for r in json.loads(response.content)['result']:
                print r[0].encode('utf-8'), r[2]
    except:
        traceback.print_exc()

image_list_path = 'qa_data.json'
url = 'http://0.0.0.0:8004/qa/search'

q = u'如何提升网络带宽'
search(q, url)
response = requests.get('http://0.0.0.0:8004/qa/get_all_questions')
