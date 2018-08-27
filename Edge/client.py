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
import rpyc

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True
######### Parse input arguments ######################
parser = argparse.ArgumentParser()

parser.add_argument("-w","--wservice",required=False,help="web service url")
parser.add_argument("-c","--camera",required=True,help="Camera host")
parser.add_argument("-l","--location",required=True,help="Location")
parser.add_argument("-i","--cameraid",required=True,help="Camera Id")
parser.add_argument("-g","--gender", required=False,default="True",help="Enable Gender")
parser.add_argument("-f","--frames", required=False,default="30",help="Number of frames to discard" )


args = vars(parser.parse_args())

url = None
is_gender = None
discard_frames = None

url = args['wservice']
cameraurl = args['camera']
location = args['location']
camera_id = args['cameraid']
is_gender = args['gender']
discard_frames = int(args['frames'])

if discard_frames == None: 
    discard_frames = 30



if cameraurl == "0":
    cameraurl = 0

############# Setup Logging #########################

logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('client')
logger.setLevel(logging.INFO)
hdlr = RotatingFileHandler('/home/pi/Desktop/signage.log',maxBytes=375000000)
logger.addHandler(hdlr)


############# Create Computer Visoin Objects ################

# Load the player
player_connection = rpyc.connect("localhost", 18861)
player_object = player_connection.root

if is_gender == "True":
    gender_connection = rpyc.connect("localhost", 18862)
    gender_object = gender_connection.root
else:
    gender_object = None


# Face detector object
detector = dlib.get_frontal_face_detector()


################################################

# Start connecting to the camera
frame_ind = 1
old_frame = None
frame = None
logger.info("Connecting to "+str(cameraurl))

cap = None
if cameraurl == 0:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
else:
    cap = rtsp.Client(cameraurl,drop_frame_limit=5, retry_connection=False, verbose=True)
    frame = cap.read()



#player_object.play_default()

while True:
    ### Wait for a fresh image
    logger.info("Camera connection is "+("opened."if cap.isOpened() else "closed."))
    old_frame = frame
    if cameraurl == 0:
        ret, frame = cap.read()
    else:
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


    # Get the frame as numpy array
    # for dlib detector    
    frame = np.asarray(frame)
    frame.setflags(write=True)

    ### Detection
    logger.info("Processing frame {}".format(frame_ind))
    dets = detector(frame, 1)
    windows = []
    people_count = 0
    logger.info("Count of faces detected: {}".format(len(dets)))

    ### Find genders if faces detected.
    if len(dets) > 0:
        male_count = 0
        female_count = 0
        for i, d in enumerate(dets):
            people_count+=1
            windows.append([d.left(), d.top(), d.right(), d.bottom()])
            cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (255, 0, 255), 2)
            crop_img = frame[d.top():d.bottom(), d.left():d.right()]
            if is_gender:
                pred_val = gender_object.process(x_test=crop_img, y_test=None, batch_size=1)
                gender = pred_val
                if gender == 'male':
                    male_count+=1
                elif gender == 'female':
                    female_count+=1

        # Switch ads based on gender        
        if male_count > female_count:
            player_object.play_male()
        else:
            player_object.play_female()


 

        logger.info(str(people_count) +  ':' + ",".join(str(r) for v in windows for r in v))

        # Upload data
        if url != None:
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
   
    # Restart the video for every 10th frame
    if frame_ind%20 == 0:
        player_object.play_default()

   # Clear the buffer
    if cameraurl != 0:
        for i in range(discard_frames):
            f = cap.read()
            f = None


    frame_limit = 500
    if frame_ind >= frame_limit:
        logger.info("Retrieved {} of frames. Stopping to help manage video buffer.".format(frame_limit))
        sys.exit(0)

