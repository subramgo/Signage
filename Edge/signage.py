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

with open("/opt/signage/credentials.yml",'r') as ymlfile:
    credentials = yaml.load(ymlfile)

logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('client')
logger.setLevel(logging.INFO)
hdlr = RotatingFileHandler(cfg.get('logfile_path','/home/pi/signage.log'),maxBytes=cfg.get('logfile_maxbytes',375000000))
logger.addHandler(hdlr)


###########################################################
##############           Interfaces           #############
###########################################################
# Ad Server
if cfg['serve_ads']:
    ad_player = None

    while not ad_player:
        try:
            ad_player = rpyc.connect(*cfg['ad server']).root
            logger.info("Connected to ad server.")
        except:
            logger.info("Waiting then trying to connect to ad service.")
            time.sleep(3)
            continue
else:
    ad_player = None
    logger.info("Ad service is disabled.")

# Gender Classifier
if cfg['gender_classification']:
    gender_object = None
    while not gender_object:
        try:
            gender_object = rpyc.connect(*cfg['gender classification']).root
            logger.info("Connected to gender classification.")
        except:
            logger.info("Waiting then trying to connect to gender service.")
            time.sleep(3)
            continue
    logger.info("Connected to gender classification.")
else:
    gender_object = None
    logger.info("Gender classification is disabled.")


# Data Server
if cfg['data_report']:
    try:
        requests.get(cfg['data_protocol']+cfg['data_address_port'])
        logger.info("Database is available.")
    except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,requests.exceptions.HTTPError) as err: 
        logger.error("Cannot reach data reporting service; "+str(err))
else:
    logger.info("Data reporting is disabled.")

def upload_faces(windows):
    if not cfg['data_report']:
        return
    protocol=cfg['data_protocol']
    uri=cfg['data_address_port']
    cred=credentials['data_uploading']
    path='/api/v2/signage/faces'

    camera_id=cfg['cam_name']
    location=cfg['cam_location_name']
    data = {
            'camera_id' : camera_id
           ,'no_faces'  : str(len(windows))
           ,'windows'   : ",".join(str(r) for v in windows for r in v)
           ,'location'  : location
            }
    headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    logger.info("Uploading detections...")
    r = requests.post(protocol+cred+"@"+uri+path,json=data,headers=headers)
    logger.info("Data upload: "+str(r))


def upload_demographics(genders):
    if not cfg['data_report']:
        return
    protocol=cfg['data_protocol']
    uri=cfg['data_address_port']
    cred=credentials['data_uploading']
    path='/api/v2/signage/demographics'

    camera_id=cfg['cam_name']
    location=cfg['cam_location_name'] 
    data = {
            'camera_id'    : camera_id
           ,'location'     : location
           ,'male_count'   : sum([1 for g in genders if g=='male'])
           ,'female_count' : sum([1 for g in genders if g=='female'])
    }
    headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    logger.info("Uploading demographics...")
    r = requests.post(protocol+cred+"@"+uri+path,json=data,headers=headers)
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

    if faces:
        logger.info("Count of faces detected: {}".format(len(faces)))
    else:
        logger.info("No faces detected.")

    return (faces,windows)

# Camera
def cam_address():
    try:
        return cfg['cam_protocol']+credentials['video_stream']+cfg['cam_stream_address']
    except:
        return 0

discard_frames = cfg.get('discard_frames',30)
cameraurl = cam_address()
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
            cap.read()

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
    if faces:
        upload_faces(windows)

        if cfg['gender_classification']:
            genders = [gender_object.process(x_test=face, y_test=None, batch_size=1) for face in faces]
            upload_demographics(genders)

        # Switch ads based on gender        
        if cfg['serve_ads']:
            if sum([1 for g in genders if g=='male']) > (len(genders)/2):
                logger.info("more males now")
                ad_player.play_male()
            else:
                logger.info("more females now")
                ad_player.play_female()


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

