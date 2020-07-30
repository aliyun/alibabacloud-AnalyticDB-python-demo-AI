# coding: utf-8
# 当demo运行时, 使用一下脚本来导入数据
import requests
import json
import multiprocessing
import traceback
def insert(q, a, url, i):
    try:
            print type(q)
            data = {
                'question': q.encode('utf-8'),
                'answer': a.encode('utf-8'),
            }
            response = requests.post(url, data)
            print response.content
            print "insert %d records"%i
    except:
        traceback.print_exc()


def run_insert(ip, port):
    image_list_path = 'qa_data.json'
    url = 'http://%s:%d/qa/insert'%(ip, port)
    with open(image_list_path, 'r') as f:
        qa_map = json.load(f, encoding='utf-8')
        i = 0
        pool_size = 5
        pool = multiprocessing.Pool(pool_size)
        for q,a in qa_map.items():
            pool.apply_async(insert, args=(q.strip(), a, url, i))
            i += 1
        pool.close()
        pool.join()

ip = '127.0.0.1'
port = 8004

run_insert(ip, port)