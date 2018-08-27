from flask import render_template, flash, redirect, Blueprint, request, send_from_directory, Response,abort,g,jsonify,url_for
import json
import numpy as np 
import cv2
from .models import  signage_db,FaceSignage, User
from .ObjectTracking import track_objects

from sqlalchemy import func
import sys
import dlib
from flask import current_app as app
import os
import time
import json

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

signage_api = Blueprint('signage', __name__, url_prefix='/api/v1/signage', template_folder = 'templates', static_folder = 'static')
face_detector = dlib.get_frontal_face_detector()



@signage_api.route('/', methods =['GET'])
@auth.login_required
def signage_page():
    signs = FaceSignage.query.order_by(FaceSignage.date_created.desc()).all()
    signs_json = json.dumps([sign.get_json() for sign in signs])
    return Response(signs_json, mimetype="application/json")
 

@signage_api.route('/object_track',methods=['GET'])
@auth.login_required
def object_track():
    signs = FaceSignage.query.order_by(FaceSignage.date_created.desc()).all()
    signs_json = [sign.get_json() for sign in signs]
    object_log = track_objects(signs_json)
    return Response(json.dumps(object_log), mimetype="application/json")



@signage_api.route('/signage_upload', methods=['POST'])
@auth.login_required
def signage_upload():
    payload = request.json
    signage_obj = FaceSignage(image_id = "image_id", no_faces = payload['no_faces'], windows = payload['windows'], 
        camera_id = payload['camera_id'], location=payload['location'])
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

@signage_api.route('/users', methods = ['POST'])
def new_user():
    payload = request.json
    print(payload['username'])
    username = payload['username']
    password = payload['password']
    print(password)
    if username is None or password is None:
        abort(400) # missing arguments
    #if User.query.filter_by(username = username).first() is not None:
    #    abort(400) # existing user
    print(username, password)
    user = User(username = username)
    user.hash_password(password)
    signage_db.session.add(user)
    signage_db.session.commit()
    return jsonify({ 'username': user.username }, 200)


