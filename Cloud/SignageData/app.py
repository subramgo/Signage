from flask import Flask 
from flask_bootstrap import Bootstrap 
from data import api_v2
from data import signage_db

from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask import render_template, flash, redirect



app = Flask(__name__)
app.config.from_object('config') 




photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


signage_db.init_app(app)
signage_db.create_all(app=app)


app.register_blueprint(api_v2)


Bootstrap(app)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Akshi')

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
