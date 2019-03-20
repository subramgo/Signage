from flask import Flask, Response
from data import api_v2
from data import signage_db

from flask import render_template, flash, redirect
import os
#import uwsgi
import psycopg2



config_name = os.getenv('FLASK_ENV', 'development')


app = Flask(__name__, instance_relative_config=True)


app.config.from_object('config')

if config_name == 'docker':
    app.config.from_pyfile('docker_config.py')


if config_name == 'production':
    app.config.from_pyfile('config.py')



signage_db.init_app(app)
signage_db.create_all(app=app)


app.register_blueprint(api_v2)




@app.route('/')
@app.route('/index')
def index():
    return Response(response={'status': 'Running app'}, status=200, mimetype="application/json")

@app.before_first_request
def setup_user():
    import yaml
    from data import signage_db, User


    with open("./web.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        username,password = cfg['upload_user'].split(':')
        user = User(username = username)
        user.hash_password(password)
        signage_db.session.add(user)
        signage_db.session.commit()
        print("added access user")
