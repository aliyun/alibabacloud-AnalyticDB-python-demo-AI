# coding: utf-8
from flask import Blueprint, jsonify, request
from flask_api import status
from sqlalchemy import create_engine, func, select, table, insert
from utils.models import db
import traceback
from logger import logger
from utils.utils import byteify, get_image_uri, get_image_thumbnail
import time
import json

qa_api = Blueprint("qa_api", __name__)
class qa_table(db.Model):
    __tablename__ = 'qa_table'
    question = db.Column(db.Text, primary_key=True)
    answer = db.Column(db.Text, nullable=False)
    feature = db.Column(db.ARRAY(db.REAL), nullable=False)

def get_text_feature(question, pipeline_name='text_feature_extractor'):
    if pipeline_name is None:
        return None

    result_set = db.engine.execute(func.open_analytic.pipeline_run_dist_random(pipeline_name, question))
    for row in result_set:
        emb = json.loads(row[0])['emb']
        return emb


def get_all_questions():
    stmt = select([qa_table.question])
    result = db.engine.execute(stmt)
    result = [r[0] for r in result]
    return result


def insert(question, answer):
    feature = get_text_feature(question)
    ins = qa_table.__table__.insert().values(question=question, answer=answer, feature=feature)
    db.engine.execute(ins)

def search(question, top_k=10):
    feature = get_text_feature(question)
    distance = func.public.l2_distance(feature, qa_table.feature)
    stmt = select([qa_table.question, qa_table.answer, distance.label('dist')])
    stmt = stmt.order_by('dist')
    stmt = stmt.limit(top_k)
    t_start = time.time()
    result = db.engine.execute(stmt)
    print time.time() - t_start
    result = [(r[0], r[1], r[2]) for r in result]
    return result

def count():
    result = db.engine.execute("select count(*) from %s"%qa_table.__tablename__)
    result = [r[0] for r in result]
    return result

@qa_api.route('/qa/get_all_questions', methods=['GET'])
def get_all_questions_api():
    try:
        result = get_all_questions()
        return jsonify({"code": status.HTTP_200_OK, "result": result, "msg": ""})
    except:
        logger.error(traceback.print_exc())
        return jsonify({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": "Internal error "})

@qa_api.route('/qa/count', methods=['GET'])
def count_api():
    try:
        result = count()
        return jsonify({"code": status.HTTP_200_OK, "result": result, "msg": ""})
    except:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"

@qa_api.route('/qa/search',  methods=['POST'])
def search_api():
    try:
        question = request.form.get('question')
        top_k = request.form.get('top_k')
        if top_k is None:
            top_k = 10

        if question is None:
            return status.HTTP_400_BAD_REQUEST, "category is not defined"
        result = search(question, top_k)
        return jsonify({"code": status.HTTP_200_OK, 'result': byteify(result), "msg": ""})
    except:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"

@qa_api.route('/qa/insert',  methods=['POST'])
def insert_api():
    try:
        question = request.form.get('question').encode('utf-8')
        print type(question)
        answer = request.form.get('answer').encode('utf-8')
        print question
        if question is None:
            return status.HTTP_400_BAD_REQUEST, "question is not defined"
        if answer is None:
            return status.HTTP_400_BAD_REQUEST, "answer is not defined"
        insert(question, answer)
        return jsonify({
            "result": "success"
        })
    except:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"
