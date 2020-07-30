# coding: utf-8
import requests
import json
import base64
import os
import random
import uuid
import multiprocessing
import traceback

def insert(image_path, url, i):
    try:
        with open(image_path, "rb") as f:

            image_name = uuid.uuid4()
            data = {
                'image': base64.b64encode(f.read()),
                'image_name': image_name,
            }
            response = requests.post(url, data)
            print "insert %d images"%i
    except:
        traceback.print_exc()

image_list_path = 'image_list.txt'
url = 'http://11.165.235.112:8004/scene_search/insert'

with open(image_list_path, 'r') as f:
    i = 0
    lines = f.readlines()
    random.shuffle(lines)
    pool_size = 10
    pool = multiprocessing.Pool(pool_size)
    for line in lines:
        pool.apply_async(insert, args=(line.strip(), url, i))
        i += 1
    pool.close()
    pool.join()