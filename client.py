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

#url ="http://0.0.0.0:5000/api/v1/signage/signage_upload"
url ="http://178.128.68.231:5000/api/v1/signage/signage_upload"


logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('async')
logger.setLevel(logging.DEBUG)

host="root:pass@192.168.1.3 "
stream = "ufirststream"

detector = dlib.get_frontal_face_detector()
cap = cv2.VideoCapture('rtsp://'+host+'/'+stream)
#cap = cv2.VideoCapture(0)
frame_ind =0
while 1:
    ret, frame = cap.read()
    if not ret:
        break


    frame_ind+=1

    logger.info("Processing frame {}".format(frame_ind))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dets, scores, idx = detector.run(frame, 1, 1)
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
    data['camera_id'] = 'camera-1'
    data['no_faces'] = str(people_count)
    data['windows'] = ",".join(str(r) for v in windows for r in v)

    payload = json.dumps(data)


    headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json=data, headers = headers)

    logger.info("Finished processing frame {}".format(frame_ind))

