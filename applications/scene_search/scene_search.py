# coding: utf-8
from flask import Blueprint, jsonify, request
from flask_api import status
import psycopg2 as pg2
from sqlalchemy import create_engine, func, select, table, insert
from utils.models import db
import traceback
import os
import base64
from logger import logger
import uuid
from utils.utils import byteify, get_image_uri, get_image_thumbnail
import time
import json

scene_search_api = Blueprint("scene_search_api", __name__)
class table(db.Model):
    __tablename__ = 'scene_table'
    image_name = db.Column(db.Text, primary_key=True)
    image_data_thumbnail = db.Column(db.LargeBinary, nullable=False)
    attributes = db.Column(db.Text, primary_key=False)
    feature = db.Column(db.ARRAY(db.REAL), nullable=False)
    def __repr__(self):
        return '<name %s>' % self.image_name

def recognize(data, pipeline_name='scene_recognition_attributes'):
    result_set = db.engine.execute(func.open_analytic.pipeline_run_dist_random(pipeline_name, data))
    for row in result_set:
        return row[0]

def search(emb, keywords, top_k=10):
    if emb is not None:
        distance = func.public.l2_distance(emb, table.feature)
        stmt = select([table.image_name, table.image_data_thumbnail, distance.label('dist'), table.attributes])
    else:
        stmt = select([table.image_name, table.image_data_thumbnail])

    stmt = stmt
    for keyword in keywords:
        stmt = stmt.where(table.attributes.like(u'%{}%'.format(keyword)))

    if emb is not None:
        stmt = stmt.order_by('dist')

    stmt = stmt.limit(top_k)
    t_start = time.time()
    result = db.engine.execute(stmt)
    print time.time() - t_start
    result = [list(r) for r in result]
    for r in result:
        print r[-1]
    return result

def count():
    result = db.engine.execute("select count(*) from %s"%table.__tablename__)
    result = [r[0] for r in result]
    return result

@scene_search_api.route('/scene_search/count', methods=['GET'])
def count_api():
    try:
        result = count()
        return jsonify({"code": status.HTTP_200_OK, "result": result, "msg": ""})
    except:
        logger.error(traceback.print_exc())
        return jsonify({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": "Internal error "})


@scene_search_api.route('/scene_search/search',  methods=['POST'])
def search_api():
    try:
        image_data = request.form.get('image')
        keywords = request.form.get('keywords')
        print keywords
        top_k = request.form.get('top_k')
        if keywords is None:
            keywords = []
        else:
            keywords = keywords.split(' ')

        if top_k is None:
            top_k = 10

        if image_data is None or len(image_data) == 0:
            emb = None
        else:
            image_data = image_data.split(',')[-1]
            image_bytes = base64.b64decode(image_data)
            image_bytes_thumbnail = get_image_thumbnail(image_bytes, (299, 299))
            data = pg2.Binary(image_bytes_thumbnail)
            result = recognize(data)
            result = json.loads(result)
            emb = result[u'features']
        result = search(emb, keywords, top_k)
        for i in range(len(result)):
            result[i][1] = get_image_uri(result[i][1])
            if emb is not None:
                result[i][2] = round(result[i][2],3)
        return jsonify({"code": status.HTTP_200_OK, 'result': byteify(result), "msg": ""})
    except:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"

@scene_search_api.route('/scene_search/insert',  methods=['POST'])
def insert_api():
    try:
        image_data = request.form.get('image')
        image_name = request.form.get('image_name')
        if image_data is None:
            return status.HTTP_400_BAD_REQUEST, "image_data is not defined"

        if image_name is None:
            image_name = str(uuid.uuid4())
        else:
            image_name = os.path.split(image_name)[-1]
        print image_name
        image_data = image_data.split(',')[-1]
        image_bytes = base64.b64decode(image_data)
        image_bytes_thumbnail = get_image_thumbnail(image_bytes, (299,299))
        data = pg2.Binary(image_bytes_thumbnail)
        result = recognize(data)
        result = json.loads(result)
        emb = result[u'features']
        attributes = result[u'attributes_str'][:5] # top 5
        scenes = result[u'scene_str'][:3]  # top 3
        attributes = u' '.join(scenes + attributes)


        ins = table.__table__.insert().values(image_name=image_name,image_data_thumbnail=image_bytes_thumbnail,
                                                   feature=emb, attributes=attributes)

        db.engine.execute(ins)
        return jsonify({
            "result": "success"
        })
    except:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"

@scene_search_api.route('/scene_search/recognize',  methods=['POST'])
def recognize_api():
    try:
        image_data = request.form.get('image')
        image_name = request.form.get('image_name')
        if image_data is None or len(image_data) == 0:
            return "image_data is not defined", status.HTTP_400_BAD_REQUEST

        if image_name is None:
            image_name = str(uuid.uuid4())
        else:
            image_name = os.path.split(image_name)[-1]
        print len(image_data), type(image_data)
        image_data = image_data.split(',')[-1]
        image_bytes = base64.b64decode(image_data)
        image_bytes_thumbnail = get_image_thumbnail(image_bytes)
        data = pg2.Binary(image_bytes_thumbnail)
        result = json.loads(recognize(data))

        attributes = result[u'attributes_str'][:5] # top 5
        scenes = result[u'scene_str'][:3] # top 3

        attributes = u'<br>'.join(attributes)
        scenes = u'<br>'.join(scenes)
        attributes = u"%s<br>%s" % (scenes, attributes)
        return jsonify({
            "result": attributes
        })
    except:
        logger.error(traceback.format_exc())
        traceback.print_exc()
        return "Internal error", status.HTTP_500_INTERNAL_SERVER_ERROR