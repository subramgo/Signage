from flask import render_template, flash, redirect, Blueprint, request, send_from_directory, Response
import json
from .models import  signage_db,FaceSignage
from .ObjectTracking import track_objects
from sqlalchemy.sql import func, text

import sys
from flask import current_app as app
import os
import time
import json

signage_api = Blueprint('signage', __name__, url_prefix='/api/v1/signage', template_folder = 'templates', static_folder = 'static')



@signage_api.route('/', methods =['GET'])
def signage_page():
    #signs = FaceSignage.query.order_by(FaceSignage.date_created.desc()).filter( (func('now') - func(FaceSignage.date_created)) <= 3)
    signs = FaceSignage.query.filter(  (  func.julianday(func.date('now')) - func.julianday(FaceSignage.date_created) )<=3 ).all()


    signs_json = json.dumps([sign.get_json() for sign in signs])
    return Response(signs_json, mimetype="application/json")
 

@signage_api.route('/object_track',methods=['GET'])
def object_track():
    #signs = FaceSignage.query.order_by(FaceSignage.date_created.desc()).all()
    signs = FaceSignage.query.filter(  (  func.julianday(func.date('now')) - func.julianday(FaceSignage.date_created) )<=3 ).all()
    signs_json = [sign.get_json() for sign in signs]
    object_log = track_objects(signs_json)
    return Response(json.dumps(object_log), mimetype="application/json")



@signage_api.route('/signage_upload', methods=['POST'])
def signage_upload():
    payload = request.json
    signage_obj = FaceSignage(image_id = "image_id", no_faces = payload['no_faces'], windows = payload['windows'], 
        camera_id = payload['camera_id'], location=payload['location'])
    signage_db.session.add(signage_obj)
    signage_db.session.commit()
    return  Response(response={'status': 'SUCCESS'}, status=200, mimetype="application/json")



