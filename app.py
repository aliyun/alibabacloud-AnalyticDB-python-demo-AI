import logging
from flask import Flask, render_template, send_from_directory
from flask_api import status
from utils.models import db
import os
from app_config import CONFIG
from applications.image_search import image_search
from applications.face_search import face_search
# from applications.dna_search import dna_search
# from applications.oss_image_analysis import oss_image_analysis

def create_db_uri(config):
    print config
    db_string = "postgres://%s:%s@%s:%s/%s"%(config['user'],
                                             config['password'],
                                             config['host'],
                                             config['port'],
                                             config['database'])
    return db_string


create_db_uri(CONFIG['database_config'])
try:
    ip = CONFIG.get('demo_config').get('host_ip')
    port = CONFIG.get('demo_config').get('host_port')
    if ip is None:
        ip = '0.0.0.0'
    if port is None:
        port = 8005
except:
    pass
    ip = '0.0.0.0'
    port = 8005

dir_path = os.path.dirname(os.path.realpath(__file__))
static_url = os.path.join(dir_path, 'front_end/dist')
app = Flask(__name__, static_url_path=static_url, template_folder=static_url)
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = create_db_uri(CONFIG['database_config'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
# app.config['SQLALCHEMY_ECHO'] = True

print create_db_uri(CONFIG['database_config'])

db.init_app(app)
db.app = app
app.register_blueprint(image_search.image_search_api)
app.register_blueprint(face_search.face_search_api)
# app.register_blueprint(dna_search.dna_search_api)
# app.register_blueprint(oss_image_analysis.oss_image_analysis_api)

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

db.create_all()
if __name__ == '__main__':
    Flask.run(app, host=ip, port=port, threaded=True)
