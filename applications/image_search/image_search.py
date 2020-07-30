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
image_search_api = Blueprint("image_search_api", __name__)
class images(db.Model):
    __tablename__ = 'image_table'
    image_name = db.Column(db.Text, primary_key=True)
    # image_data = db.Column(db.LargeBinary, nullable=False)
    image_data_thumbnail = db.Column(db.LargeBinary, nullable=False)
    feature = db.Column(db.ARRAY(db.REAL), nullable=False)
    def __repr__(self):
        return '<name %s>' % self.image_name

def get_feature(data):
    feature = \
        cast(
            func.pg_catalog.TRANSLATE(
                cast(
                    cast(func.open_analytic.pipeline_run_dist_random('general_feature_extractor', data),
                         sqlalchemy.types.JSON)[
                        'feature'],
                    sqlalchemy.types.TEXT
                ),
                '[]',
                '{}'
            ),
            sqlalchemy.types.ARRAY(sqlalchemy.types.REAL)
        )
    return feature

def init():
    result_set = db.engine.execute("select 1 from open_analytic.current_pipelines where name = 'general_feature_extractor'")
    if result_set.rowcount == 0:
        result_set = db.engine.execute(func.open_analytic.pipeline_create('general_feature_extractor'))
        for r in result_set:
            print r

def insert(image_name, image_bytes):

    image_bytes_thumbnail = get_image_thumbnail(image_bytes)
    data = pg2.Binary(image_bytes_thumbnail)
    feature = get_feature(data)
    ins = images.__table__.insert().values(image_name=image_name, image_data_thumbnail=image_bytes_thumbnail, feature=select([feature]))
    db.engine.execute(ins)


def search(image_bytes, top_k=10):
    image_bytes = get_image_thumbnail(image_bytes)
    data = pg2.Binary(image_bytes)
    feature_query = get_feature(data)
    # distance = func.public.l2_distance(feature_query, images.feature)
    result = db.engine.execute(select([feature_query]))
    for row in result:
        feature_val = row[0]
    distance = func.public.l2_distance(feature_val, images.feature)
    stmt = select([images.image_name, images.image_data_thumbnail, distance.label('dist')]).order_by('dist').limit(top_k)
    t_start = time.time()
    result = db.engine.execute(stmt)
    print time.time() - t_start
    result = [list(r) for r in result]
    return result

def count():
    result = db.engine.execute("select count(*) from %s"%images.__tablename__)
    result = [r[0] for r in result]
    return result

def clear(engine):
    pass

def destroy(engine):
    pass


@image_search_api.route('/image_search/search',  methods=['POST', 'GET'])
def search_api():
    try:
        t_start = time.time()
        image_data = request.form.get('image')
        top_k = request.form.get('top_k')
        if image_data is None:
            return jsonify({"code": status.HTTP_400_BAD_REQUEST,
                            "msg": "image data is missing"})
        image_data = image_data.split(',')[-1]
        image_bytes = base64.b64decode(image_data)
        init()
        result = search(image_bytes, top_k)
        print time.time() - t_start
        for i in range(len(result)):
            result[i][1] = get_image_uri(result[i][1])
            result[i][2] = round(result[i][2],3)
        print time.time() - t_start

        return jsonify({"code": status.HTTP_200_OK, 'result': byteify(result), "msg": ""})
    except:
        traceback.print_exc()
        return jsonify({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": "Internal error "})


@image_search_api.route('/image_search/insert', methods=['POST', 'GET'])
def insert_api():
    try:
        image_data = request.form.get('image')
        image_name = request.form.get('image_name')
        if image_data is None:
            return jsonify({"code": status.HTTP_400_BAD_REQUEST,
                            "msg": "image data is missing"})
        if image_name is None:
            image_name = str(uuid.uuid4())
        else:
            image_name = os.path.split(image_name)[-1]
        image_data = image_data.split(',')[-1]
        image_bytes = base64.b64decode(image_data)
        init()
        insert(image_name, image_bytes)
    except:
        logger.error(traceback.print_exc())
        return jsonify({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": "Internal error "})
    result = []
    return jsonify({"code": status.HTTP_200_OK, 'result': result, "msg": ""})

@image_search_api.route('/image_search/init')
def image_search_init():
    try:
        init()
    except:
        logger.error(traceback.print_exc())
        return jsonify({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": "Internal error "})
    return jsonify({"code": status.HTTP_200_OK, "msg": ""})

@image_search_api.route('/image_search_clear')
def image_search_clear():
    result = []
    return jsonify({"code": status.HTTP_200_OK, 'result': result, "msg": ""})

@image_search_api.route('/image_search_destroy')
def image_search_destroy():
    result = []
    return jsonify({"code": status.HTTP_200_OK, 'result': result, "msg": ""})

@image_search_api.route('/image_search/count', methods=['GET'])
def count_api():
    try:
        result = count()
        return jsonify({"code": status.HTTP_200_OK, "result": result, "msg": ""})
    except:
        logger.error(traceback.print_exc())
        return jsonify({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": "Internal error "})




