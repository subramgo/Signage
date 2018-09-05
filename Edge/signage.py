"""
    Signage Edge Operations
      * IP camera client
      * orchestrates image services
      * reports resulting data to Signage database

    Also does:
      * face detection
"""

import logging
from logging.handlers import RotatingFileHandler
import sys
import cv2
import dlib
import requests
import requests.exceptions
import yaml
import numpy as np
import time
import rtsp
import rpyc

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

###########################################################
##############         Configuration         ##############
###########################################################
with open("/boot/signage/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('client')
logger.setLevel(logging.INFO)
hdlr = RotatingFileHandler(cfg.get('logfile_path','/home/pi/Desktop/signage.log'),maxBytes=cfg.get('logfile_maxbytes',375000000))
logger.addHandler(hdlr)


###########################################################
##############           Interfaces           #############
###########################################################
# Ad Server
if cfg['serve_ads']:
    ad_player = rpyc.connect(*cfg['ad server']).root
    logger.info("Connected to ad server.")
else:
    logger.info("Ad service is disabled.")

# Gender Classifier
if cfg['gender_classification']:
    gender_connection = rpyc.connect(*cfg['gender classification'])
    gender_object = gender_connection.root
    logger.info("Connected to gender classification.")
else:
    gender_object = None
    logger.info("Gender classification is disabled.")


# Data Server
data_uri = cfg['data_reporting_uri']
try:
    requests.get(data_uri)
    logger.info("Database is available.")
except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,requests.exceptions.HTTPError) as err: 
    logger.error("Cannot reach data reporting service; "+str(err))

def upload_data(camera_id,people_count,windows,location):
    data = {
            'camera_id' : camera_id
           ,'no_faces'  : str(people_count)
           ,'windows'   : ",".join(str(r) for v in windows for r in v)
           ,'location'  : location
            }
    headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    logger.info("Uploading detections...")
    r = requests.post(data_uri,json=data,headers=headers)
    logger.info("Data upload: "+str(r))


# Face Detector
detector = dlib.get_frontal_face_detector()


def detect_faces(frame):
    dets = detector(frame, 1)
    windows = []
    faces = []
    for i, d in enumerate(dets):
        windows.append([d.left(), d.top(), d.right(), d.bottom()])
        cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (255, 0, 255), 2)
        faces.append(frame[d.top():d.bottom(), d.left():d.right()])

    logger.info("Count of faces detected: {}".format(len(faces)))

    return (faces,windows)

# Camera
discard_frames = cfg.get('discard_frames',30)
cameraurl = cfg.get('cam_uri',0) # default to USB Cam
frame_ind = 1
old_frame = None
frame = None
logger.info("Connecting to "+str(cameraurl))

cap = rtsp.Client(cameraurl,drop_frame_limit=5, retry_connection=False, verbose=True)

_old_frame = None

def grab_frame():
    # Clear the buffer
    # TODO remove this when rtsp package supports is
    global _old_frame
    if cameraurl != 0:
        for i in range(discard_frames):
            f = cap.read()
            f = None

    logger.info("Camera connection is "+("opened."if cap.isOpened() else "closed."))

    frame = cap.read()

    while frame == _old_frame or not cap.isOpened():
        logger.error("No new image yet.")
        time.sleep(3)
        frame = cap.read()
        if not cap.isOpened():
            logger.info("Attempting reconnect to "+cameraurl+"...")
            cap.open(cameraurl)
    logger.info("Grabbed new image")
    _old_frame = frame
    return frame

###########################################################
##############          Orchestration         #############
###########################################################
while True:
    logger.info("Processing frame {}".format(frame_ind))
    frame = grab_frame()

    # for dlib detector    
    frame = np.asarray(frame)
    frame.setflags(write=True)

    ### Detection
    faces, windows = detect_faces(frame)
    
    ### Find genders if faces detected.
    if faces and cfg['gender_classification']:
        genders = [gender_object.process(x_test=face, y_test=None, batch_size=1) for face in faces]

        # Switch ads based on gender        
        if cfg['serve_ads']:
            if sum([1 for g in genders if g=='male']) > (len(genders)/2):
                logger.info("more males now")
                ad_player.play_male()
            else:
                logger.info("more females now")
                ad_player.play_female()

        # Upload data
        upload_data(camera_id=cfg['cam_name']
                  , people_count=len(faces)
                  , windows=windows
                  , location=cfg['cam_location_name'])

    logger.info("Finished processing frame {}".format(frame_ind))
    frame_ind+=1
   
    # Restart the video for every 10th frame
    # TODO remove this when ad player supports it
    if frame_ind%20 == 0:
        ad_player.play_default()

    frame_limit = 500
    if frame_ind >= frame_limit:
        logger.info("Retrieved {} frames. Stopping to help manage video buffer.".format(frame_limit))
        sys.exit(0)

