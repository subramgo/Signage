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

import config
import data
import demographics
import ads
import faces
import camera


###########################################################
##############         Configuration         ##############
###########################################################

cfg_defaults = { 
      'camera'                : {
          'enabled'           : False
        , 'stream_address'    : '192.168.1.168/usecondstream'
        , 'protocol'          : 'rtsp://'
        , 'location_name'     : 'signage-analysis-demo'
        , 'name'              : 'signage-camera-1'
        , 'credentials'       : '*user*:*pass*'
    }
    
    , 'logging'               : {
          'enabled'           : True
        , 'logfile_path'      : 'signage.log'
        , 'logfile_maxbytes'  : 375000000
    }
 
    , 'ads'                   : {
          'enabled'           : False
        , 'server'            : ['localhost',18861]
        , 'rotation'          : 0
        , 'window'            : (400,0,400,480)
    }

    , 'data'                  : {
          'enabled'           : False
        , 'credentials'       : '*user*:*pass*'
        , 'data_server'       : '127.0.0.1:5000'
        , 'data_protocol'     : 'http://'
    }

    , 'demographics'          : {
          'enabled'           : False
        , 'server'            : ['localhost',18862]
    }
    }

cfg = config.Config(
      filepath = "/boot/signage/config.yml"
    , description = "Orchestration and Image Feed"
    , dictionary = cfg_defaults
    , internalpath = "/opt/signage/credentials.yml")

cfg.mask('data.credentials'   ,'*user*:*pass*')
cfg.mask('camera.credentials' ,'*user*:*pass*')

if cfg['logging']['enabled']:
    print("Logging to {}".format(cfg['logging']['logfile_path']))
    hdlr = RotatingFileHandler(cfg['logging']['logfile_path'],maxBytes=cfg['logging']['logfile_maxbytes'])
else:
    print("No logging.")
    hdlr = logging.NullHandler()
logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('SignageEdge)')
logger.setLevel(logging.INFO)
logger.addHandler(hdlr)


###########################################################
##############           Interfaces           #############
###########################################################
camera = camera.CamClient(logger,cfg['camera'])
face_detector = faces.FaceDetector(logger)
dataClient = data.DataClient(logger,cfg['data'])
ads = ads.get_client(logger,cfg['ads'])
demographics = demographics.get_client(logger,cfg['demographics'])

def dprint(processed_output):
    # print results of `process` for human readers
    rpt = "Demographics on faces: "
    rpt += ", ".join(["{} aged {}".format(gender,age) for gender,age in processed_output])
    rpt += "."
    return rpt

###########################################################
##############          Orchestration         #############
###########################################################
def main():
    while True:
        frame = camera.grab_frame()

        ### Detection
        faces, windows = face_detector.detect_faces(frame)
        
        ### Find genders if faces detected.
        if faces:
            dataClient.upload_faces(windows)

            if demographics:
                _demographics = [(demographics.process(x_test=face, y_test=None, batch_size=1)) for face in faces]
                logger.info(dprint(_demographics))
                dataClient.upload_demographics(_demographics)

                # Switch ads based on demographics        
                if ads:
                    ads.demographics(_demographics)
       
        # Restart the video for every 10th frame
        # TODO remove this when ad player supports it
        if camera.frame_ind%20 == 0:
            if ads:
                ads.play_default()

        frame_limit = 500
        if camera.frame_ind >= frame_limit:
            logger.info("Retrieved {} frames. Stopping to help manage video buffer.".format(frame_limit))
            sys.exit(0)


if __name__ == "__main__":
    main()
