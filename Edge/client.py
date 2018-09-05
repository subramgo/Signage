"""
Mock up a video feed pipeline
"""
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import sys
import cv2
import dlib
import requests
from PIL import Image
from io import BytesIO
import json
import argparse

import numpy as np
import time
import rtsp

from Gender import GenderClassifier
gender = GenderClassifier()

from Player import Player
player_object = Player()


parser = argparse.ArgumentParser()

parser.add_argument("-w","--wservice",required=False,help="web service url")
parser.add_argument("-c","--camera",required=True,help="Camera host")
parser.add_argument("-l","--location",required=True,help="Location")
parser.add_argument("-i","--cameraid",required=True,help="Camera Id")
parser.add_argument("-g","--gender", required=False,default="True",help="Enable Gender")


args = vars(parser.parse_args())

url = None
is_gender = None

url = args['wservice']
cameraurl = args['camera']
location = args['location']
camera_id = args['cameraid']
is_gender = args['gender']

if cameraurl == "0":
    cameraurl = 0

logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('client')
logger.setLevel(logging.INFO)
hdlr = RotatingFileHandler('/home/pi/Desktop/signage.log',maxBytes=375000000)
logger.addHandler(hdlr)

detector = dlib.get_frontal_face_detector()
#cap = cv2.VideoCapture(cameraurl)
frame_ind = 1
old_frame = None
logger.info("Connecting to "+cameraurl)

cap = rtsp.Client(cameraurl,drop_frame_limit=5, retry_connection=False, verbose=True)
frame = cap.read()

while True:
    ### Wait for a fresh image
    logger.info("Camera connection is "+("opened."if cap.isOpened() else "closed."))
    old_frame = frame
    frame = cap.read()
    if frame == old_frame or not cap.isOpened():
        logger.error("No new image yet.")
        time.sleep(3)
        if not cap.isOpened():
            logger.info("Attempting reconnect to "+cameraurl+"...")
            cap.open(cameraurl)
        continue
    else:
        logger.info("Grabbed new image")

    ### Input processing: PIL Image -> ???
    frame = np.asarray(cap.read())
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Gender Classification
    if is_gender == "True":
        image_arr = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        pred_val = predictor.process(x_test=image_arr, y_test=None, batch_size=1)
        if pred_val == "male":
            player.play_male()
        else:
            player.play_female()


    frame.setflags(write=True)

    ### Detection
    logger.info("Processing frame {}".format(frame_ind))
    dets = detector(frame, 1)
    windows = []
    people_count = 0
    logger.info("Count of faces detected: {}".format(len(dets)))

    ### Upload results if people were found
    if len(dets) > 0:
        for i, d in enumerate(dets):
            people_count+=1
            windows.append([d.left(), d.top(), d.right(), d.bottom()])

        logger.info(str(people_count) +  ':' + ",".join(str(r) for v in windows for r in v))

        data = {}
        data['camera_id'] = camera_id
        data['no_faces'] = str(people_count)
        data['windows'] = ",".join(str(r) for v in windows for r in v)
        data['location'] = location
        payload = json.dumps(data)
        headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        logger.info("Uploading detections...")
        r = requests.post(url, json=data, headers = headers)
        logger.info("Data upload: "+str(r))

    logger.info("Finished processing frame {}".format(frame_ind))
    frame_ind+=1
    if frame_ind%20 == 0:
        player_object.play_default()

    for i in range(25):
        f = cap.read()
        f = None
        
    frame_limit = 500
    if frame_ind >= frame_limit:
        logger.info("Retrieved {} of frames. Stopping to help manage video buffer.".format(frame_limit))
        sys.exit(0)

