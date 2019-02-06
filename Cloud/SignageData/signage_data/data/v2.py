from flask import Blueprint, request, Response, abort, g, jsonify
import json
from ..models import signage_db,FaceSignage,Demographics,User
from ..ObjectTracking import track_objects
from ..DistanceMeasure import find_distance
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



############ Face Count Services #####################################


def return_faces():
    signs = FaceSignage.query.all()
    signs_json = [sign.get_json() for sign in signs]
    signs_json = find_distance(signs_json)

    return signs_json

@signage_v2.route('/faces/live/<location>', methods =['GET'])
@auth.login_required
def get_faces_live(location):
    """
    Return the latest data (maxdate)for a given location
    """
    maxdate = FaceSignage.query.filter(FaceSignage.location == location)\
    .with_entities(func.max(FaceSignage.date_created)).first()[0]
    maxdate = maxdate.replace(hour=0, minute=0, second=0)
    
    signs = FaceSignage.query\
    .filter(FaceSignage.location == location , FaceSignage.date_created >= maxdate)\
    .all()

    signs_json = [sign.get_json() for sign in signs]
    signs_json = find_distance(signs_json)

    return Response(json.dumps(signs_json), mimetype="application/json")


@signage_v2.route('/faces', methods =['GET'])
@auth.login_required
def get_faces():
    """
    Return all the faces data. If available in cache return from cache else fetch.
    """
    signs_json = cache.get('signs-json')
    if signs_json is None:
        signs_json = return_faces()
        cache.set('signs-json', signs_json, timeout = TIMEOUT)
    return Response(json.dumps(signs_json), mimetype="application/json")


@signage_v2.route('/faces', methods=['POST'])
@auth.login_required
def post_faces():
    """
    Post face data
    """
    payload = request.json
    signage_obj = FaceSignage(image_id = "image_id", no_faces = payload['no_faces'], windows = payload['windows'], 
        camera_id = payload['camera_id'], location=payload['location'])
    signage_db.session.add(signage_obj)
    signage_db.session.commit()
    return  Response(response={'status': 'SUCCESS'}, status=200, mimetype="application/json")


############# Activity Services #######################################
# Activity takes face data ( no_faces and face windows) and returns
# time alive information

def calculate_activity():
    signs = FaceSignage.query.order_by(FaceSignage.date_created.desc()).all()
    signs_json = [sign.get_json() for sign in signs]
    object_log = track_objects(signs_json)

    return object_log

@signage_v2.route('/activity/live/<location>', methods =['GET'])
@auth.login_required
def get_activity_live(location):
    """
    Return the latest data (maxdate)for a given location
    """
    maxdate = FaceSignage.query.filter(FaceSignage.location == location)\
    .with_entities(func.max(FaceSignage.date_created)).first()[0]
    maxdate = maxdate.replace(hour=0, minute=0, second=0)
    signs_json = FaceSignage.query\
    .filter(FaceSignage.location == location , FaceSignage.date_created >= maxdate)\


    signs_json = [sign.get_json() for sign in signs_json]
    object_log = track_objects(signs_json)

    return Response(json.dumps(object_log), mimetype="application/json")

@signage_v2.route('/activity',methods=['GET'])
@auth.login_required
def get_activity():
    object_log = cache.get('object-log')
    if object_log is None:
        object_log = calculate_activity()
        cache.set('object-log', object_log, timeout = TIMEOUT)
    return Response(json.dumps(object_log), mimetype="application/json")



################# Demograhics Services ###################################

def return_demographics():
    demographics = Demographics.query.all()
    list_json = [demo.get_json() for demo in demographics]
    return list_json

@signage_v2.route('/demographics', methods=['GET'])
@auth.login_required
def get_demographics():
    object_log = cache.get('demographics')
    
    if object_log is None:
        object_log = return_demographics()
        cache.set('demographics-log', object_log, timeout = TIMEOUT)


    return Response(json.dumps(object_log), mimetype="application/json")


@signage_v2.route('/demographics', methods=['POST'])
@auth.login_required
def post_demographics():
    payload = request.json
    signage_obj = Demographics(male_count=payload['male_count'], female_count=payload['female_count'], 
        camera_id = payload['camera_id'], location=payload['location'], 
        gender_list=payload['gender_list'],age_list=payload['age_list'])
    signage_db.session.add(signage_obj)
    signage_db.session.commit()
    return  Response(response={'status': 'SUCCESS'}, status=200, mimetype="application/json")


@signage_v2.route('/demographics/live/<location>', methods =['GET'])
@auth.login_required
def get_demograhics_count_live(location):
    maxdate = Demographics.query.filter(Demographics.location == location)\
    .with_entities(func.max(Demographics.date_created)).first()[0]
    maxdate = maxdate.replace(hour=0, minute=0, second=0)
    
    demographics = Demographics.query\
    .filter(Demographics.location == location , Demographics.date_created >= maxdate)\
    .all()

    list_json = [demo.get_json() for demo in demographics]


    return Response(json.dumps(list_json), mimetype="application/json")


################### Password Service #######################################


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

