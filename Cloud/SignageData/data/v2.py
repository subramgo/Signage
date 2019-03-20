from flask import Blueprint, request, Response, abort, g, jsonify
import json
from .models import signage_db, Person,User, Signage, Enterprise, Store
import datetime
from flask_httpauth import HTTPBasicAuth
from werkzeug.contrib.cache import SimpleCache
from sqlalchemy import func, and_
from flask import current_app as app


auth = HTTPBasicAuth()
cache = SimpleCache()

signage_v2 = Blueprint('signage2', __name__, url_prefix='/api/v2/signage', 
    template_folder = 'templates', static_folder = 'static')

TIMEOUT=10


############ Store service #######################################

@signage_v2.route('/store/all/<enterpriseid>', methods=['GET'])
@auth.login_required
def get_all_stores(enterpriseid):
    store = Store.query.filter(Store.enterprise_id == enterpriseid)
    signages_json = [sign.json for sign in store]
    return Response(signages_json, mimetype="application/json")

@signage_v2.route('/store/<storeid>', methods=['GET'])
@auth.login_required
def get_stores(storeid):
    store = Store.query.filter(Store.id == storeid)
    signages_json = [sign.json for sign in store]
    return Response(signages_json, mimetype="application/json")


############ Signage Services #####################################
@signage_v2.route('/signage/<storeid>', methods=['GET'])
@auth.login_required
def get_signages(storeid):
    store = Signage.query.filter(Signage.store_id == storeid)
    signages_json = [sign.json for sign in store]
    return Response(signages_json, mimetype="application/json")

############ Person Services #####################################


def return_person(signageid):
    signs = Person.query.filter(Person.signage_id == signageid)
    #signs_json = [sign.get_json() for sign in signs]
    signs_json = [sign.json for sign in signs]

    return signs_json






@signage_v2.route('/person/live/<signageid>', methods =['GET'])
@auth.login_required
def get_faces_live(signageid):
    """
    Return the latest data (maxdate)for a given location
    """
    maxdate = Person.query.filter(Person.signage_id == signageid)\
    .with_entities(func.max(Person.date_created)).first()[0]
    
    maxdate = maxdate.replace(hour=0, minute=0, second=0)
    
    signs = Person.query\
    .filter(Person.signageid == signageid , Person.date_created >= maxdate)\
    .all()

    signs_json = [sign.json for sign in signs]

    return Response(signs_json, mimetype="application/json")


@signage_v2.route('/person/<signageid>', methods =['GET'])
@auth.login_required
def get_faces(signageid):
    """
    Return all the faces data. If available in cache return from cache else fetch.
    """
    signs_json = cache.get('signs-json')
    if signs_json is None:
        signs_json = return_person(signageid)
        cache.set('signs-json', signs_json, timeout = TIMEOUT)
    
    return Response(signs_json, mimetype="application/json")


@signage_v2.route('/person/upload', methods=['POST'])
@auth.login_required
def post_faces():
    """
    Post face data
    """
    payload = request.json
    ## Check if the face_id exist already
    ### if exist, update time alive
    person = Person.query.filter_by(face_id = payload['face_id']).first()
    if person is not None:
        person.time_alive = payload['time_alive']
    else:

        signage_obj = Person( age = payload['age'], 
            camera_id = payload['camera_id'], location=payload['location'],
            time_alive = payload['time_alive'], gender=payload['gender'], 
            engagement_range=payload['engagement_range'],face_id=payload['face_id'],signage_id=payload['signage_id'])
        
        signage_db.session.add(signage_obj)
    
    signage_db.session.commit()
    return  Response(response={'status': 'SUCCESS'}, status=200, mimetype="application/json")



################### Password Service #######################################


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

