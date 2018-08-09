"""
Mock up a video feed pipeline
"""
import asyncio
import logging
import sys
import cv2
import dlib
import requests
from PIL import Image
from io import BytesIO
import json
import argparse
import time
import rtsp

parser = argparse.ArgumentParser()

parser.add_argument("-w","--wservice",required=True,help="web service url")
parser.add_argument("-c","--camera",required=True,help="Camera host")
parser.add_argument("-l","--location",required=True,help="Location")
parser.add_argument("-i","--cameraid",required=True,help="Camera Id")


args = vars(parser.parse_args())

url = args['wservice']
cameraurl = args['camera']
location = args['location']
camera_id = args['cameraid']


if cameraurl == "0":
    cameraurl = 0

logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('async')
logger.setLevel(logging.DEBUG)


detector = dlib.get_frontal_face_detector()
cap = cv2.VideoCapture(cameraurl)
#cap = rtsp.Client(cameraurl)
frame_ind =0
frames = []
while 1:
    for i in range(15):
        ret,frame = cap.read()
        if ret:
            frames.append(frame)

    frames = []
    ret,frame = cap.read()
    if  ret:
        frame_ind+=1
        """
        cv2.imshow('image',frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        """
        logger.info("Processing frame {}".format(frame_ind))
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dets= detector(frame, 1)
        windows = []
        people_count = 0
        logger.info("No faces detected {}".format(len(dets)))
        if len(dets) > 0:
            for i, d in enumerate(dets):
                people_count+=1
                windows.append([d.left(), d.top(), d.right(), d.bottom()])

        logger.info(str(people_count) +  ':' + ",".join(str(r) for v in windows for r in v))

        # Make the payload
        data = {}
        data['camera_id'] = camera_id
        data['no_faces'] = str(people_count)
        data['windows'] = ",".join(str(r) for v in windows for r in v)
        data['location'] = location

        payload = json.dumps(data)


        headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, json=data, headers = headers)

        logger.info("Finished processing frame {}".format(frame_ind))

