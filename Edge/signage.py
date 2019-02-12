#!python3

"""
    Signage Edge Operations
      * IP camera client
      * orchestrates image services
      * reports resulting data to Signage database

    Also does:
      * face detection
"""

import sys
import time

import log
import data
import demographics
import ads
import faces
import camera
import sharedconfig

###########################################################
##############           Interfaces           #############
###########################################################
cfg = sharedconfig.cfg

def get_interfaces():
    refresh()

    logger = log.get_logger(cfg['logging'])
    _camera = camera.CamClient(logger,cfg['camera'])
    face_detector = faces.FaceDetector(logger)
    dataClient = data.DataClient(logger,cfg['data'],cfg['camera'])
    adserver = ads.get_client(logger,cfg['ads'])
    demo = demographics.DemographicsClassifier(logger,cfg['demographics'])

    return logger,_camera,face_detector,dataClient,adserver,demo


###########################################################
##############          Orchestration         #############
###########################################################
def refresh():
    """ Check configuration files for new settings and update interfaces """
    global cfg
    cfg.load()

def main():
    logger,camera,face_detector,dataClient,adserver,demo = get_interfaces()

    while cfg['camera']['enabled']:
        frame = camera.grab_frame()

        ### Detection
        faces, windows = face_detector.detect_faces(frame)

        ### Find genders if faces detected
        if faces:

            dataClient.upload_windows(windows)

            measures = demo.process(faces)
            
            dataClient.upload_demographics(measures)

            try:
                adserver.demographics(measures)
            except:
                logger.error("Ad server was disconnected.")
                adserver = ads.get_client(logger,cfg['ads'])

        time.sleep(5)
        refresh()

if __name__ == "__main__":
    main()
