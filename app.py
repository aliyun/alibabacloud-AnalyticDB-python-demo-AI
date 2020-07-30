# coding: utf-8
import logging
from flask import Flask, render_template, Response, send_from_directory, jsonify, request, redirect, url_for
from flask_api import status
from utils.models import db
import os
from app_config import CONFIG
from applications.image_search import image_search
# from applications.dna_search import dna_search
# from applications.oss_image_analysis import oss_image_analysis
from applications.face_search import face_search
from applications.item_search import item_search
from applications.scene_search import scene_search
from applications.qa import qa
from sqlalchemy import func

def create_db_uri(config):
    print config
    db_string = "postgres://%s:%s@%s:%s/%s"%(config['user'],
                                             config['password'],
                                             config['host'],
                                             config['port'],
                                             config['database'])
    return db_string


create_db_uri(CONFIG['database_config'])
# ip = '127.0.0.1'
ip = '0.0.0.0'
demo_config = CONFIG.get('demo_config')
if demo_config is not None:
    port = demo_config.get('host_port')
else:
    port = None

if port is None:
    port = 8004
dir_path = os.path.dirname(os.path.realpath(__file__))
static_url = os.path.join(dir_path, 'front_end/dist')
app = Flask(__name__, static_url_path=static_url, template_folder=static_url)
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = create_db_uri(CONFIG['database_config'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

print create_db_uri(CONFIG['database_config'])

db.init_app(app)
db.app = app
app.register_blueprint(image_search.image_search_api)
# app.register_blueprint(dna_search.dna_search_api)
# app.register_blueprint(oss_image_analysis.oss_image_analysis_api)
app.register_blueprint(face_search.face_search_api)
app.register_blueprint(item_search.item_search_api)
app.register_blueprint(scene_search.scene_search_api)
app.register_blueprint(qa.qa_api)

def create_pipeline(pipeline_name):
    result_set = db.engine.execute(
        "select 1 from open_analytic.current_pipelines where name = '%s'"%pipeline_name)
    if result_set.rowcount == 0:
        db.session.begin()
        print("creating pipeline %s..."%pipeline_name)
        db.session.execute(func.open_analytic.pipeline_create(pipeline_name))
        for r in result_set:
            print r
        db.session.commit()

# pipelines = ['female_cloth_recognizer', 'male_cloth_recognizer', 'child_cloth_recognizer', 'shoe_recognizer', 'bag_recognizer']
pipelines = ['scene_recognition_attributes']

for pipeline_name in pipelines:
    create_pipeline(pipeline_name)

db.create_all()

# qa.insert('1+1=?', '2')
# result = qa.search(u'忘记密码怎么办')
# for row in result:
#     print type(row[0])
#     print row[0].encode('utf-8'), row[2]

# # db.session.begin()
# result_set = db.session.execute(func.open_analytic.pipeline_create('shoe_recognizer'))
# # db.engine.commit()
# for r in result_set:
#     print r
# db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def page(path):
    return send_from_directory(app.static_url_path, path)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    Flask.run(app, host=ip, port=port, threaded=True)
