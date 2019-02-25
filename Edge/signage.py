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
import sharedconfig
import camera
import detection
import distance
import demographics
import tracking
import data
import ads


###########################################################
##############          Orchestration         #############
###########################################################

def main():
    cfg = sharedconfig.cfg

    logger = log.get_logger(cfg['logging'])
    cam = camera.CamClient(logger,cfg['camera'])
    face_detector = detection.FaceDetector(logger)
    radar = distance.DistanceMeasurer(cfg['camera'])
    demog = demographics.DemographicsClassifier(logger,cfg['demographics'])
    tracker = tracking.ObjectTracker(cfg['tracking'])
    dataClient = data.DataClient(logger,cfg)
    adserver = ads.get_client(logger,cfg['ads'])

    while True:
        if not cfg['camera']['enabled']:
            time.sleep(5)
            continue

        frame = cam.grab_frame()

        ### Detection
        faces = face_detector.detect_faces(frame)

        ### Audience measurement when faces detected
        if faces:
            distances = radar.measure(faces,frame)

            ids,live_times = tracker.track(faces)

            genders,ages = demog.process(faces)

            measures = [Measure(a,b,c,d,e) for a,b,c,d,e in zip(ids,live_times,distances,genders,ages)]
            logger.info(' , '.join([str(m) for m in measures]))

            dataClient.upload(measures)

            try:
                adserver.demographics(measures)
            except:
                logger.error("Ad server was disconnected.")
                adserver = ads.get_client(logger,cfg['ads'])

        else:
            tracker.track(faces)
            logger.info("No faces detected.")

        cfg.load()

class Measure:
    """ An Audience Measure """
    def __init__(self,face_id,time_alive,engagement_range,gender,age):
        self.iduid = face_id
        self.time_alive = time_alive
        self.engagement_range = engagement_range
        self.gender = gender
        self.age = age

    def __str__(self):
        report = "ID: {} - {},{} - lived {} secs - range {}".format(self.iduid,self.age,self.gender,self.time_alive,self.engagement_range)
        return report

if __name__ == "__main__":
    main()
