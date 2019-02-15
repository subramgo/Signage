#!python3

"""
    Signage Edge Operations
      * IP camera client
      * orchestrates image services
      * reports resulting data to Signage database

    Also does:
      * face detection
"""

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
    cam = camera.CamClient(logger,cfg['camera'])
    face_detector = faces.FaceDetector(logger)
    dataClient = data.DataClient(logger,cfg['data'],cfg['camera'])
    demo = demographics.DemographicsClassifier(logger,cfg['demographics'])
    adserver = ads.get_client(logger,cfg['ads'])

    return logger,cam,face_detector,dataClient,adserver,demo


###########################################################
##############          Orchestration         #############
###########################################################
def refresh():
    """ Check configuration files for new settings and update interfaces """
    global cfg
    cfg.load()

def main():
    logger,cam,face_detector,dataClient,adserver,demo = get_interfaces()

    while True:
        if not cfg['camera']['enabled']:
            time.sleep(5)
            continue

        frame = cam.grab_frame()

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

        else:
            logger.info("No faces detected.")

        refresh()

if __name__ == "__main__":
    main()
