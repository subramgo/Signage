from flask import Blueprint, request, Response, abort, g, jsonify
import json

from ..models import signage_db,FaceSignage,Demographics,User
from ..ObjectTracking import track_objects
import datetime
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


signage_v2 = Blueprint('signage2', __name__, url_prefix='/api/v2/signage', template_folder = 'templates', static_folder = 'static')



tday = datetime.datetime.now()
lday = tday - datetime.timedelta(days=7)
limit = lday.timestamp()

@signage_v2.route('/faces', methods =['GET'])
@auth.login_required
def get_faces():
    signs = FaceSignage.query.filter(FaceSignage.date_created >= limit).order_by(FaceSignage.date_created.desc()).all()
    signs_json = json.dumps([sign.get_json() for sign in signs])
    return Response(signs_json, mimetype="application/json")


@signage_v2.route('/faces', methods=['POST'])
@auth.login_required
def post_faces():
    payload = request.json
    signage_obj = FaceSignage(image_id = "image_id", no_faces = payload['no_faces'], windows = payload['windows'], 
        camera_id = payload['camera_id'], location=payload['location'])
    signage_db.session.add(signage_obj)
    signage_db.session.commit()
    return  Response(response={'status': 'SUCCESS'}, status=200, mimetype="application/json")


@signage_v2.route('/activity',methods=['GET'])
@auth.login_required
def get_activity():
    signs = FaceSignage.query.filter(FaceSignage.date_created >= limit).order_by(FaceSignage.date_created.desc()).all()
    signs_json = [sign.get_json() for sign in signs]
    object_log = track_objects(signs_json)
    return Response(json.dumps(object_log), mimetype="application/json")


#@signage_v2.route('/activity', methods=['POST'])
#@auth.login_required
#def post_activity():
#    payload = request.json
#    signage_obj = FaceSignage(image_id = "image_id", no_faces = payload['no_faces'], windows = payload['windows'], 
#        camera_id = payload['camera_id'], location=payload['location'])
#    signage_db.session.add(signage_obj)
#    signage_db.session.commit()
#    return  Response(response={'status': 'SUCCESS'}, status=200, mimetype="application/json")


@signage_v2.route('/demographics', methods=['GET'])
@auth.login_required
def get_demographics():
    demographics = Demographics.query.filter(Demographics.date_created >= limit).order_by(Demographics.date_created.desc()).all()
    list_json = [demo.get_json() for demo in demographics]
    return Response(json.dumps(list_json), mimetype="application/json")


@signage_v2.route('/demographics', methods=['POST'])
@auth.login_required
def post_demographics():
    payload = request.json
    signage_obj = Demographics(male_count=payload['male_count'], female_count=payload['female_count'], 
        camera_id = payload['camera_id'], location=payload['location'], gender_list=payload['gender_list'],age_list=payload['age_list'])
    signage_db.session.add(signage_obj)
    signage_db.session.commit()
    return  Response(response={'status': 'SUCCESS'}, status=200, mimetype="application/json")


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    print(user)
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

