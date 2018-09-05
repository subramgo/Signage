from flask import Flask 
from flask_bootstrap import Bootstrap 
from .signage.signage import signage_api
from .signage.models import signage_db

from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask import render_template, flash, redirect



app = Flask(__name__)
app.config.from_object('config') 

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


signage_db.init_app(app)
signage_db.create_all(app=app)

# Signage
app.register_blueprint(signage_api, url_prefix='/api/v1/signage')


Bootstrap(app)


@app.route('/')
@app.route('/index')
def index():
  user ={'name':'Gopi'}
  return render_template('index.html', title='Akshi', user=user)



