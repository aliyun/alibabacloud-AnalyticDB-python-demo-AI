# coding: utf-8
from flask import Blueprint, jsonify, request
from flask_api import status
import sqlalchemy
from sqlalchemy.dialects.postgresql import BYTEA
import psycopg2 as pg2
from sqlalchemy import create_engine, func, select, table, insert
from sqlalchemy import Table, Column, String, MetaData
from utils.models import db
from sqlalchemy.sql.expression import cast
import traceback
import io
import os
import base64
from logger import logger
import uuid
from utils.utils import byteify, get_image_uri, get_image_thumbnail
import time
import json

item_search_api = Blueprint("item_search_api", __name__)
class item_table(db.Model):
    __tablename__ = 'item_table'
    image_name = db.Column(db.Text, primary_key=True)
    category = db.Column(db.Text, nullable=False)
    # image_data = db.Column(db.LargeBinary, nullable=False)
    image_data_thumbnail = db.Column(db.LargeBinary, nullable=False)
    attributes = db.Column(db.Text, primary_key=False)
    feature = db.Column(db.ARRAY(db.REAL), nullable=False)
    def __repr__(self):
        return '<name %s>' % self.image_name

cat_pipeline_map = {
    u'女装': 'female_cloth_recognizer',
    u'男装': 'male_cloth_recognizer',
    u'童装': 'child_cloth_recognizer',
    u'鞋靴': 'shoe_recognizer',
    u'箱包': 'bag_recognizer'
}

def recognize(data, category):
    pipeline_name = cat_pipeline_map.get(category)
    print pipeline_name
    if pipeline_name is None:
        return None
    result_set = db.engine.execute(func.open_analytic.pipeline_run_dist_random(pipeline_name, data))
    for row in result_set:
        return row[0]

def search(category, emb, keywords, top_k=10):
    if emb is not None:
        distance = func.public.l2_distance(emb, item_table.feature)
        stmt = select([item_table.image_name, item_table.image_data_thumbnail, distance.label('dist')])
    else:
        stmt = select([item_table.image_name, item_table.image_data_thumbnail])

    stmt = stmt.where(item_table.category==category)

    for keyword in keywords:
        stmt = stmt.where(item_table.attributes.like(u'%{}%'.format(keyword)))

    if emb is not None:
        stmt = stmt.order_by('dist')

    stmt = stmt.limit(top_k)
    t_start = time.time()
    result = db.engine.execute(stmt)
    print time.time() - t_start
    result = [list(r) for r in result]
    return result

def count():
    result = db.engine.execute("select count(*) from %s"%item_table.__tablename__)
    result = [r[0] for r in result]
    return result

@item_search_api.route('/item_search/count', methods=['GET'])
def count_api():
    try:
        result = count()
        return jsonify({"code": status.HTTP_200_OK, "result": result, "msg": ""})
    except:
        logger.error(traceback.print_exc())
        return jsonify({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": "Internal error "})
@item_search_api.route('/item_search/search',  methods=['POST'])
def search_api():
    try:
        image_data = request.form.get('image')
        category = request.form.get('category')
        keywords = request.form.get('keywords')
        top_k = request.form.get('top_k')
        if keywords is None:
            keywords = []
        else:
            keywords = keywords.split(' ')

        if category is None:
            return status.HTTP_400_BAD_REQUEST, "category is not defined"

        if top_k is None:
            top_k = 10

        if image_data is None or len(image_data) == 0:
            emb = None
        else:
            image_data = image_data.split(',')[-1]
            image_bytes = base64.b64decode(image_data)
            image_bytes_thumbnail = get_image_thumbnail(image_bytes, (299, 299))
            data = pg2.Binary(image_bytes_thumbnail)
            result = recognize(data, category)
            result = json.loads(result)[u'result']
            emb = result[u'emb']
        result = search(category, emb, keywords, top_k)
        for i in range(len(result)):
            result[i][1] = get_image_uri(result[i][1])
            if emb is not None:
                result[i][2] = round(result[i][2],3)

        return jsonify({"code": status.HTTP_200_OK, 'result': byteify(result), "msg": ""})
    except:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"

@item_search_api.route('/item_search/insert',  methods=['POST'])
def insert_api():
    try:
        image_data = request.form.get('image')
        image_name = request.form.get('image_name')
        category = request.form.get('category')
        if category is None:
            return status.HTTP_400_BAD_REQUEST, "category is not defined"
        if image_data is None:
            return status.HTTP_400_BAD_REQUEST, "image_data is not defined"

        if image_name is None:
            image_name = str(uuid.uuid4())
        else:
            image_name = os.path.split(image_name)[-1]

        print image_name, category

        image_data = image_data.split(',')[-1]
        image_bytes = base64.b64decode(image_data)
        image_bytes_thumbnail = get_image_thumbnail(image_bytes, (299,299))
        data = pg2.Binary(image_bytes_thumbnail)
        result = recognize(data, category)
        result = json.loads(result)[u'result']
        emb = result[u'emb']
        leaf_category = result[u'categoryName']
        props = result[u'properties']

        attributes_list = []
        for prop in props:
            name = prop[u'propertyName']
            valueName=prop[u'valueName']
            attributes_list.append(u'%s:%s'%(name, valueName))

        attributes = u' '.join(attributes_list)
        attributes = u"%s %s"%(leaf_category, attributes)

        ins = item_table.__table__.insert().values(image_name=image_name, category=category,
                                                   image_data_thumbnail=image_bytes_thumbnail,
                                                   feature=emb, attributes=attributes)
        db.engine.execute(ins)
        return jsonify({
            "result": "success"
        })
    except:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"

@item_search_api.route('/item_search/recognize',  methods=['POST'])
def recognize_api():
    try:
        image_data = request.form.get('image')
        image_name = request.form.get('image_name')
        category = request.form.get('category')
        if category is None:
            return  "category is not defined", status.HTTP_400_BAD_REQUEST
        if image_data is None or len(image_data) == 0:
            return "image_data is not defined", status.HTTP_400_BAD_REQUEST

        if image_name is None:
            image_name = str(uuid.uuid4())
        else:
            image_name = os.path.split(image_name)[-1]
        print category
        print len(image_data), type(image_data)
        image_data = image_data.split(',')[-1]
        image_bytes = base64.b64decode(image_data)
        image_bytes_thumbnail = get_image_thumbnail(image_bytes)
        data = pg2.Binary(image_bytes_thumbnail)
        result = recognize(data, category)

        result = json.loads(result)[u'result']
        leaf_category = result[u'categoryName']
        props = result[u'properties']
        attributes_list = []
        for prop in props:
            name = prop[u'propertyName']
            valueName = prop[u'valueName']
            attributes_list.append(u'%s:%s' % (name, valueName))

        attributes = u'<br>'.join(attributes_list)
        attributes = u"%s<br>%s" % (leaf_category, attributes)
        return jsonify({
            "result": attributes
        })
    except:
        logger.error(traceback.format_exc())
        traceback.print_exc()
        return "Internal error", status.HTTP_500_INTERNAL_SERVER_ERROR

